// Authentication Guard - Include this in all protected pages
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

// Display logged-in user info
function displayUserInfo() {
    const authData = requireAuth();
    if (authData) {
        const userInfoElement = document.getElementById('userInfo');
        if (userInfoElement) {
            userInfoElement.innerHTML = `
                <span class="user-welcome">
                    <i class="fas fa-user-circle"></i> ${authData.userName}
                </span>
            `;
        }
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', () => {
    requireAuth();
    displayUserInfo();
});
