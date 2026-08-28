// Dashboard JS
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.endsWith('dashboard.html')) {
        loadDashboardStats();
    }
});

async function loadDashboardStats() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const welcomeEl = document.getElementById('welcome-user-name');
    if (welcomeEl && user.name) {
        welcomeEl.textContent = user.name;
    }

    try {
        const stats = await apiRequest('/dashboard/stats');

        // Update cards
        document.getElementById('stat-total-trips').textContent = stats.total_trips;
        document.getElementById('stat-active-trips').textContent = stats.active_trips;
        document.getElementById('stat-total-expenses').textContent = formatCurrency(stats.total_expenses_amount);
        document.getElementById('stat-amount-paid').textContent = formatCurrency(stats.user_total_paid);
        document.getElementById('stat-amount-owe').textContent = formatCurrency(stats.user_total_owe);
        document.getElementById('stat-amount-receive').textContent = formatCurrency(stats.user_total_receive);

        // Render Recent Trips
        renderRecentTrips(stats.recent_trips);

        // Render Recent Expenses
        renderRecentExpenses(stats.recent_expenses);

    } catch (err) {
        console.error('Failed to load dashboard stats:', err);
        showToast('Failed to load dashboard metrics.', 'danger');
    }
}

function renderRecentTrips(trips) {
    const container = document.getElementById('recent-trips-container');
    if (!container) return;

    if (!trips || trips.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-map-marked-alt fa-3x mb-3 text-secondary opacity-50"></i>
                <p>No trips created yet. Click "Create New Trip" to get started!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `<div class="row row-cols-1 row-cols-md-2 g-3">` + trips.map(t => `
        <div class="col">
            <div class="card card-custom h-100">
                <img src="${t.image_url || 'images/mountains.jpg'}" class="trip-card-img" alt="${t.name}">
                <div class="card-body p-3">
                    <h5 class="card-title fw-bold mb-1">
                        <a href="trip-details.html?id=${t.id}" class="text-decoration-none text-dark">${t.name}</a>
                    </h5>
                    <p class="text-muted small mb-2">
                        <i class="fas fa-map-marker-alt text-danger me-1"></i>${t.destination} <br>
                        <i class="fas fa-calendar-alt text-primary me-1"></i>${t.start_date} to ${t.end_date}
                    </p>
                    <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top">
                        <div class="small fw-bold text-secondary">
                            <i class="fas fa-users text-info me-1"></i>${t.members_count || 0} Members
                        </div>
                        <div class="small fw-bold text-primary">
                            ${formatCurrency(t.total_expense_amount || 0)}
                        </div>
                    </div>
                </div>
                <div class="card-footer bg-white border-0 p-3 pt-0">
                    <a href="trip-details.html?id=${t.id}" class="btn btn-sm btn-outline-primary w-100 fw-semibold">
                        View Details <i class="fas fa-arrow-right ms-1"></i>
                    </a>
                </div>
            </div>
        </div>
    `).join('') + `</div>`;
}

function renderRecentExpenses(expenses) {
    const container = document.getElementById('recent-expenses-container');
    if (!container) return;

    if (!expenses || expenses.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-receipt fa-3x mb-3 text-secondary opacity-50"></i>
                <p>No recent expenses recorded.</p>
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
                        <th>Title</th>
                        <th>Category</th>
                        <th>Paid By</th>
                        <th>Date</th>
                        <th class="text-end">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    ${expenses.map(e => `
                        <tr>
                            <td class="fw-bold">${e.title}</td>
                            <td>
                                <span class="badge badge-category ${categoryBadgeMap[e.category] || 'badge-other'}">
                                    ${e.category}
                                </span>
                            </td>
                            <td>${e.paid_by_name}</td>
                            <td class="text-muted small">${e.expense_date}</td>
                            <td class="text-end fw-bold text-primary">${formatCurrency(e.amount)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}
