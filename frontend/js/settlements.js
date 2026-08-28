// Settlements and Summary Analytics JS
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tripId = urlParams.get('id');
    if (tripId) {
        loadSettlementsAndCharts(tripId);
    }
});

let categoryChartInstance = null;
let memberChartInstance = null;

window.refreshSettlementsAndCharts = function (tripId) {
    loadSettlementsAndCharts(tripId);
};

async function loadSettlementsAndCharts(tripId) {
    try {
        const summary = await apiRequest(`/trips/${tripId}/summary`);

        renderBalancesTable(summary.member_balances);
        renderSettlementsList(summary.settlements);
        renderCategoryChart(summary.category_breakdown);
        renderMemberChart(summary.member_balances);

    } catch (err) {
        console.error('Failed to load settlements and charts:', err);
    }
}

function renderBalancesTable(balances) {
    const container = document.getElementById('balances-table-container');
    if (!container) return;

    if (!balances || balances.length === 0) {
        container.innerHTML = '<p class="text-muted">No member balance data available.</p>';
        return;
    }

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover table-custom align-middle">
                <thead>
                    <tr>
                        <th>Member Name</th>
                        <th class="text-end">Total Paid</th>
                        <th class="text-end">Total Share</th>
                        <th class="text-end">Net Balance</th>
                        <th class="text-center">Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${balances.map(b => {
                        const isCreditor = b.balance > 0.01;
                        const isDebtor = b.balance < -0.01;
                        const balanceClass = isCreditor ? 'text-success fw-bold' : isDebtor ? 'text-danger fw-bold' : 'text-muted';
                        const badgeText = isCreditor ? `Gets ${formatCurrency(b.balance)}` : isDebtor ? `Owes ${formatCurrency(Math.abs(b.balance))}` : 'Settled';
                        const badgeBg = isCreditor ? 'bg-success' : isDebtor ? 'bg-danger' : 'bg-secondary';

                        return `
                            <tr>
                                <td class="fw-bold">${b.member_name}</td>
                                <td class="text-end">${formatCurrency(b.total_paid)}</td>
                                <td class="text-end">${formatCurrency(b.total_share)}</td>
                                <td class="text-end ${balanceClass}">
                                    ${b.balance > 0 ? '+' : ''}${formatCurrency(b.balance)}
                                </td>
                                <td class="text-center">
                                    <span class="badge ${badgeBg} p-2">${badgeText}</span>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderSettlementsList(settlements) {
    const container = document.getElementById('settlements-list-container');
    if (!container) return;

    if (!settlements || settlements.length === 0) {
        container.innerHTML = `
            <div class="alert alert-success text-center fw-bold p-3">
                <i class="fas fa-check-circle me-2"></i>All expenses are settled! No payments required.
            </div>
        `;
        return;
    }

    container.innerHTML = settlements.map(s => `
        <div class="settlement-item d-flex justify-content-between align-items-center flex-wrap gap-2">
            <div class="d-flex align-items-center gap-2 fs-6">
                <span class="fw-bold text-danger">${s.from_member_name}</span>
                <i class="fas fa-long-arrow-alt-right text-muted mx-2 fs-5"></i>
                <span class="fw-bold text-success">${s.to_member_name}</span>
            </div>
            <div class="fs-5 fw-bold text-primary">
                ${formatCurrency(s.amount)}
            </div>
        </div>
    `).join('');
}

function renderCategoryChart(categoryBreakdown) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx) return;

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    if (!categoryBreakdown || categoryBreakdown.length === 0) {
        ctx.parentNode.innerHTML = '<p class="text-muted text-center py-4">No expense categories to display.</p>';
        return;
    }

    const labels = categoryBreakdown.map(c => c.category);
    const data = categoryBreakdown.map(c => c.amount);

    const backgroundColors = [
        '#ef4444', '#06b6d4', '#f59e0b', '#8b5cf6', '#10b981', '#64748b'
    ];

    categoryChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors.slice(0, labels.length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function renderMemberChart(memberBalances) {
    const ctx = document.getElementById('memberChart');
    if (!ctx) return;

    if (memberChartInstance) {
        memberChartInstance.destroy();
    }

    if (!memberBalances || memberBalances.length === 0) {
        ctx.parentNode.innerHTML = '<p class="text-muted text-center py-4">No member data to display.</p>';
        return;
    }

    const labels = memberBalances.map(m => m.member_name);
    const paidData = memberBalances.map(m => m.total_paid);
    const shareData = memberBalances.map(m => m.total_share);

    memberChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Paid',
                    data: paidData,
                    backgroundColor: '#4f46e5'
                },
                {
                    label: 'Total Share',
                    data: shareData,
                    backgroundColor: '#06b6d4'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
