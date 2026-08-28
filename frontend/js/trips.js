// Trip & Member Management JS
document.addEventListener('DOMContentLoaded', () => {
    setupCreateTripForm();
    setupTripDetailsPage();
});

/**
 * Handle Create Trip Form Logic
 */
function setupCreateTripForm() {
    const form = document.getElementById('create-trip-form');
    if (!form) return;

    const addMemberBtn = document.getElementById('add-member-input-btn');
    const memberInputsContainer = document.getElementById('member-inputs-container');

    if (addMemberBtn && memberInputsContainer) {
        addMemberBtn.addEventListener('click', () => {
            const memberRow = document.createElement('div');
            memberRow.className = 'row g-2 mb-2 member-input-row';
            memberRow.innerHTML = `
                <div class="col-md-6">
                    <input type="text" class="form-control member-name-input" placeholder="Member Name" required>
                </div>
                <div class="col-md-5">
                    <input type="email" class="form-control member-email-input" placeholder="Member Email (Optional)">
                </div>
                <div class="col-md-1 d-flex align-items-center">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-member-row-btn">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;

            memberRow.querySelector('.remove-member-row-btn').addEventListener('click', () => {
                memberRow.remove();
            });

            memberInputsContainer.appendChild(memberRow);
        });
    }

    // Handle Cover Image Theme Selection
    const themeCards = document.querySelectorAll('.trip-theme-card');
    const selectedImageInput = document.getElementById('selected_image_url');

    themeCards.forEach(card => {
        card.addEventListener('click', () => {
            themeCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            const imgPath = card.getAttribute('data-img');
            if (selectedImageInput) {
                selectedImageInput.value = imgPath;
            }
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('trip_name').value;
        const destination = document.getElementById('destination').value;
        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;
        const description = document.getElementById('description').value;
        const image_url = selectedImageInput ? selectedImageInput.value : 'images/mountains.jpg';

        // Collect extra members
        const memberRows = document.querySelectorAll('.member-input-row');
        const members = [];
        memberRows.forEach(row => {
            const mName = row.querySelector('.member-name-input').value.trim();
            const mEmail = row.querySelector('.member-email-input').value.trim();
            if (mName) {
                members.push({ name: mName, email: mEmail });
            }
        });

        try {
            const data = await apiRequest('/trips', 'POST', {
                name,
                destination,
                start_date: startDate,
                end_date: endDate,
                description,
                image_url,
                members
            });

            showToast('Trip created successfully!', 'success');
            setTimeout(() => {
                window.location.href = `trip-details.html?id=${data.trip.id}`;
            }, 1000);

        } catch (err) {
            showToast(err.message || 'Failed to create trip.', 'danger');
        }
    });
}

/**
 * Handle Single Trip Details Page Logic
 */
async function setupTripDetailsPage() {
    if (!window.location.pathname.endsWith('trip-details.html')) return;

    const urlParams = new URLSearchParams(window.location.search);
    const tripId = urlParams.get('id');

    if (!tripId) {
        showToast('No trip ID specified.', 'danger');
        setTimeout(() => window.location.href = 'dashboard.html', 1500);
        return;
    }

    try {
        const data = await apiRequest(`/trips/${tripId}`);
        const trip = data.trip;

        // Store active trip globally for other tabs
        window.currentTrip = trip;

        // Populate Header & Info
        document.getElementById('trip-title').textContent = trip.name;
        document.getElementById('trip-destination').textContent = trip.destination;
        document.getElementById('trip-dates').textContent = `${trip.start_date} to ${trip.end_date}`;
        document.getElementById('trip-description').textContent = trip.description || 'No description provided.';
        document.getElementById('trip-creator').textContent = trip.creator_name;

        const bannerEl = document.getElementById('trip-banner');
        if (bannerEl) {
            bannerEl.style.backgroundImage = `url('${trip.image_url || 'images/mountains.jpg'}')`;
        }

        // Render Members Tab
        renderMembersList(trip.members, trip.is_creator);

        // Setup Add Member Form inside Modal/Inline
        setupAddMemberForm(tripId);

    } catch (err) {
        showToast(err.message || 'Failed to load trip details.', 'danger');
    }
}

function renderMembersList(members, isCreator) {
    const container = document.getElementById('members-list-container');
    if (!container) return;

    if (!members || members.length === 0) {
        container.innerHTML = '<p class="text-muted">No members in this trip yet.</p>';
        return;
    }

    container.innerHTML = `
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
            ${members.map(m => `
                <div class="col">
                    <div class="card card-custom h-100 p-3">
                        <div class="d-flex align-items-center justify-content-between">
                            <div class="d-flex align-items-center">
                                <div class="avatar bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-3" style="width:42px; height:42px; font-weight:bold;">
                                    ${m.name.charAt(0).toUpperCase()}
                                </div>
                                <div>
                                    <h6 class="fw-bold mb-0">${m.name}</h6>
                                    <small class="text-muted">${m.email || 'No email provided'}</small>
                                </div>
                            </div>
                            ${isCreator ? `
                                <button class="btn btn-outline-danger btn-sm border-0 remove-member-btn" data-id="${m.id}" title="Remove Member">
                                    <i class="fas fa-trash-alt"></i>
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    // Attach click listeners for delete member
    container.querySelectorAll('.remove-member-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const memberId = e.currentTarget.getAttribute('data-id');
            if (confirm('Are you sure you want to remove this member?')) {
                try {
                    await apiRequest(`/members/${memberId}`, 'DELETE');
                    showToast('Member removed successfully!', 'success');
                    setupTripDetailsPage(); // reload page
                } catch (err) {
                    showToast(err.message || 'Failed to remove member.', 'danger');
                }
            }
        });
    });
}

function setupAddMemberForm(tripId) {
    const form = document.getElementById('add-member-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const name = document.getElementById('new_member_name').value.trim();
        const email = document.getElementById('new_member_email').value.trim();

        try {
            await apiRequest(`/trips/${tripId}/members`, 'POST', { name, email });
            showToast('Member added successfully!', 'success');

            // Close modal if open
            const modalEl = document.getElementById('addMemberModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();
            }

            form.reset();
            setupTripDetailsPage(); // Refresh details

        } catch (err) {
            showToast(err.message || 'Failed to add member.', 'danger');
        }
    });
}
