// Auth helper functions and listeners
document.addEventListener('DOMContentLoaded', () => {
    checkAuthState();
    setupAuthForms();
});

function checkAuthState() {
    const token = localStorage.getItem('jwt_token');
    const userJson = localStorage.getItem('user');

    const publicPages = ['index.html', 'login.html', 'register.html', ''];
    const currentPath = window.location.pathname.split('/').pop();

    if (!token && !publicPages.includes(currentPath)) {
        window.location.href = 'login.html';
        return;
    }

    if (token && (currentPath === 'login.html' || currentPath === 'register.html')) {
        window.location.href = 'dashboard.html';
        return;
    }

    // Populate user profile info in navbar if logged in
    if (userJson) {
        try {
            const user = JSON.parse(userJson);
            const navUserName = document.getElementById('nav-user-name');
            if (navUserName) {
                navUserName.textContent = user.name;
            }
        } catch (e) {
            console.error('Failed to parse cached user object');
        }
    }
}

function setupAuthForms() {
    // Register Form Listener
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (password !== confirmPassword) {
                showToast('Passwords do not match.', 'danger');
                return;
            }

            try {
                const data = await apiRequest('/register', 'POST', {
                    name,
                    email,
                    password,
                    confirm_password: confirmPassword
                });

                localStorage.setItem('jwt_token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                showToast('Registration successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);
            } catch (err) {
                showToast(err.message || 'Registration failed.', 'danger');
            }
        });
    }

    // Login Form Listener
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const data = await apiRequest('/login', 'POST', { email, password });
                localStorage.setItem('jwt_token', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                showToast('Login successful!', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 800);
            } catch (err) {
                showToast(err.message || 'Login failed.', 'danger');
            }
        });
    }

    // Logout Action
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('jwt_token');
            localStorage.removeItem('user');
            showToast('Logged out successfully.', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 800);
        });
    }
}
