// Expense Management JS
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.endsWith('trip-details.html') || window.location.pathname.endsWith('expenses.html')) {
        setupExpensesModule();
    }
});

let currentTripId = null;
let tripMembers = [];

async function setupExpensesModule() {
    const urlParams = new URLSearchParams(window.location.search);
    currentTripId = urlParams.get('id');

    if (!currentTripId) return;

    try {
        // Fetch trip members for dropdowns & checkboxes
        const membersData = await apiRequest(`/trips/${currentTripId}/members`);
        tripMembers = membersData.members || [];

        populateMemberDropdowns(tripMembers);
        loadExpenses();

        // Setup Event Listeners for Filters & Modals
        setupExpenseFilters();
        setupAddExpenseForm();

    } catch (err) {
        console.error('Error initializing expenses module:', err);
    }
}

function populateMemberDropdowns(members) {
    const paidBySelect = document.getElementById('expense_paid_by');
    const sharedByContainer = document.getElementById('expense_shared_by_container');

    if (paidBySelect) {
        paidBySelect.innerHTML = members.map(m => `
            <option value="${m.id}">${m.name}</option>
        `).join('');
    }

    if (sharedByContainer) {
        sharedByContainer.innerHTML = `
            <div class="form-check mb-2 pb-2 border-bottom">
                <input class="form-check-input" type="checkbox" id="select-all-shared" checked>
                <label class="form-check-label fw-bold text-primary" for="select-all-shared">
                    Select All Members
                </label>
            </div>
            ${members.map(m => `
                <div class="form-check">
                    <input class="form-check-input shared-member-checkbox" type="checkbox" value="${m.id}" id="share_member_${m.id}" checked>
                    <label class="form-check-label" for="share_member_${m.id}">
                        ${m.name}
                    </label>
                </div>
            `).join('')}
        `;

        // Toggle Select All
        const selectAllCheckbox = document.getElementById('select-all-shared');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = sharedByContainer.querySelectorAll('.shared-member-checkbox');
                checkboxes.forEach(cb => cb.checked = e.target.checked);
            });
        }
    }
}

async function loadExpenses() {
    const container = document.getElementById('expenses-list-container');
    if (!container) return;

    const category = document.getElementById('filter-category')?.value || 'All';
    const search = document.getElementById('filter-search')?.value || '';
    const sort = document.getElementById('filter-sort')?.value || 'date_desc';

    try {
        const queryParams = new URLSearchParams({ category, search, sort }).toString();
        const data = await apiRequest(`/trips/${currentTripId}/expenses?${queryParams}`);
        const expenses = data.expenses || [];

        renderExpensesTable(expenses, container);

        // Also trigger settlement & chart refresh if settlements script is loaded
        if (typeof window.refreshSettlementsAndCharts === 'function') {
            window.refreshSettlementsAndCharts(currentTripId);
        }

    } catch (err) {
        container.innerHTML = `<div class="alert alert-danger">Failed to load expenses: ${err.message}</div>`;
    }
}

function renderExpensesTable(expenses, container) {
    if (expenses.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-receipt fa-4x text-muted opacity-50 mb-3"></i>
                <h5>No Expenses Found</h5>
                <p class="text-muted">Click "Add Expense" to log costs for this trip.</p>
            </div>
        `;
        return;
    }

    const categoryBadgeMap = {
        'Food': 'badge-food',
        'Travel': 'badge-travel',
        'Hotel': 'badge-hotel',
        'Shopping': 'badge-shopping',
        'Entertainment': 'badge-entertainment',
        'Other': 'badge-other'
    };

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover table-custom align-middle">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Title & Notes</th>
                        <th>Category</th>
                        <th>Paid By</th>
                        <th>Shared By</th>
                        <th class="text-end">Amount</th>
                        <th class="text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${expenses.map(e => `
                        <tr>
                            <td class="text-nowrap small text-muted">${e.expense_date}</td>
                            <td>
                                <div class="fw-bold">${e.title}</div>
                                ${e.notes ? `<small class="text-muted">${e.notes}</small>` : ''}
                            </td>
                            <td>
                                <span class="badge badge-category ${categoryBadgeMap[e.category] || 'badge-other'}">
                                    ${e.category}
                                </span>
                            </td>
                            <td class="fw-semibold text-dark">${e.paid_by_name}</td>
                            <td>
                                <small class="text-muted">
                                    ${e.shares.map(s => s.member_name).join(', ')} (${e.shares.length})
                                </small>
                            </td>
                            <td class="text-end fw-bold text-primary fs-6">${formatCurrency(e.amount)}</td>
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-primary me-1 edit-expense-btn" data-expense='${JSON.stringify(e)}' title="Edit">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger delete-expense-btn" data-id="${e.id}" title="Delete">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    // Attach Listeners
    container.querySelectorAll('.delete-expense-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const expenseId = e.currentTarget.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this expense?')) {
                try {
                    await apiRequest(`/expenses/${expenseId}`, 'DELETE');
                    showToast('Expense deleted!', 'success');
                    loadExpenses();
                } catch (err) {
                    showToast(err.message || 'Failed to delete expense.', 'danger');
                }
            }
        });
    });

    container.querySelectorAll('.edit-expense-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const expenseData = JSON.parse(e.currentTarget.getAttribute('data-expense'));
            openEditExpenseModal(expenseData);
        });
    });
}

function setupExpenseFilters() {
    const categorySelect = document.getElementById('filter-category');
    const searchInput = document.getElementById('filter-search');
    const sortSelect = document.getElementById('filter-sort');

    if (categorySelect) categorySelect.addEventListener('change', loadExpenses);
    if (searchInput) searchInput.addEventListener('input', debounce(loadExpenses, 300));
    if (sortSelect) sortSelect.addEventListener('change', loadExpenses);
}

function setupAddExpenseForm() {
    const form = document.getElementById('add-expense-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const expenseId = document.getElementById('expense_id')?.value;
        const title = document.getElementById('expense_title').value.trim();
        const amount = document.getElementById('expense_amount').value;
        const category = document.getElementById('expense_category').value;
        const paid_by_member_id = document.getElementById('expense_paid_by').value;
        const expense_date = document.getElementById('expense_date').value;
        const notes = document.getElementById('expense_notes').value.trim();

        // Collect shared member checkboxes
        const checkboxes = document.querySelectorAll('.shared-member-checkbox:checked');
        const shared_member_ids = Array.from(checkboxes).map(cb => parseInt(cb.value));

        if (shared_member_ids.length === 0) {
            showToast('Please select at least one member to share the expense.', 'danger');
            return;
        }

        try {
            const body = {
                title,
                amount: parseFloat(amount),
                category,
                paid_by_member_id: parseInt(paid_by_member_id),
                expense_date,
                shared_member_ids,
                notes
            };

            if (expenseId) {
                // Update
                await apiRequest(`/expenses/${expenseId}`, 'PUT', body);
                showToast('Expense updated successfully!', 'success');
            } else {
                // Create
                await apiRequest(`/trips/${currentTripId}/expenses`, 'POST', body);
                showToast('Expense added successfully!', 'success');
            }

            // Close Modal
            const modalEl = document.getElementById('addExpenseModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }

            form.reset();
            if (document.getElementById('expense_id')) {
                document.getElementById('expense_id').value = '';
            }

            loadExpenses();

        } catch (err) {
            showToast(err.message || 'Failed to save expense.', 'danger');
        }
    });
}

function openEditExpenseModal(expense) {
    document.getElementById('expense_id').value = expense.id;
    document.getElementById('expense_title').value = expense.title;
    document.getElementById('expense_amount').value = expense.amount;
    document.getElementById('expense_category').value = expense.category;
    document.getElementById('expense_paid_by').value = expense.paid_by_member_id;
    document.getElementById('expense_date').value = expense.expense_date;
    document.getElementById('expense_notes').value = expense.notes || '';

    // Check shared members
    const sharedIds = expense.shares.map(s => s.member_id);
    document.querySelectorAll('.shared-member-checkbox').forEach(cb => {
        cb.checked = sharedIds.includes(parseInt(cb.value));
    });

    const modalTitle = document.getElementById('expenseModalLabel');
    if (modalTitle) modalTitle.textContent = 'Edit Expense';

    const modalEl = document.getElementById('addExpenseModal');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}

// Simple debounce helper
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
