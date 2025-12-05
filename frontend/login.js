// Authentication System
const API_URL = 'http://localhost:8000';

// Check if user is already logged in
function checkAuthentication() {
    const authData = sessionStorage.getItem('authData');
    if (authData) {
        // User is logged in, redirect to dashboard
        window.location.href = 'dashboard.html';
    }
}

// Verify authentication (for protected pages)
function requireAuth() {
    const authData = sessionStorage.getItem('authData');
    if (!authData) {
        // Not logged in, redirect to login
        window.location.href = 'index.html';
        return null;
    }
    return JSON.parse(authData);
}

// Logout function
function logout() {
    sessionStorage.removeItem('authData');
    window.location.href = 'index.html';
}

// Login form handler
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    checkAuthentication();
    
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const userId = document.getElementById('userId').value;
            const password = document.getElementById('password').value;
            const department = window.DEPARTMENT_TYPE || 'agriculture';

            try {
                const response = await fetch(`${API_URL}/api/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        password: password,
                        department: department
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    showAlert('success', `Login successful! Welcome, ${data.user.name}`);
                    
                    // Store authentication data
                    const authData = {
                        userId: data.user.id,
                        userName: data.user.name,
                        department: data.user.department,
                        loginTime: new Date().toISOString()
                    };
                    sessionStorage.setItem('authData', JSON.stringify(authData));
                    
                    // Redirect to dashboard after 1 second
                    setTimeout(() => {
                        window.location.href = 'dashboard.html';
                    }, 1000);
                } else {
                    showAlert('error', data.detail || 'Invalid credentials');
                }
            } catch (error) {
                showAlert('error', 'Network error. Please ensure the backend server is running.');
            }
        });
    }
});

function showAlert(type, message) {
    const alertContainer = document.getElementById('alertContainer');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        if (type !== 'success') {
            alertContainer.innerHTML = '';
        }
    }, 5000);
}
