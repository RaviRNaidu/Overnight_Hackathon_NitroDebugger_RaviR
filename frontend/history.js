// Application History Dashboard
const API_URL = 'http://localhost:8002';

let allApplications = [];

// Load applications on page load
document.addEventListener('DOMContentLoaded', () => {
    loadApplications();
    
    // Add search functionality
    document.getElementById('searchInput').addEventListener('input', filterApplications);
    document.getElementById('statusFilter').addEventListener('change', filterApplications);
});

// Load all applications from backend
async function loadApplications() {
    try {
        const response = await fetch(`${API_URL}/api/applications`);
        
        if (response.ok) {
            allApplications = await response.json();
            displayApplications(allApplications);
            updateStatistics(allApplications);
        } else {
            showAlert('error', 'Failed to load applications');
            document.getElementById('historyTableBody').innerHTML = '<tr><td colspan="10" class="error">Failed to load applications</td></tr>';
        }
    } catch (error) {
        showAlert('error', 'Network error. Please ensure the backend server is running.');
        document.getElementById('historyTableBody').innerHTML = '<tr><td colspan="10" class="error">Network error. Please check if backend is running.</td></tr>';
    }
}

// Display applications in table
function displayApplications(applications) {
    const tbody = document.getElementById('historyTableBody');
    const noDataMessage = document.getElementById('noDataMessage');
    
    if (applications.length === 0) {
        tbody.innerHTML = '';
        noDataMessage.style.display = 'block';
        return;
    }
    
    noDataMessage.style.display = 'none';
    
    tbody.innerHTML = applications.map(app => `
        <tr>
            <td><strong>${app.application_id}</strong></td>
            <td>${app.farmer_name}</td>
            <td>${app.mobile_number}</td>
            <td>${app.state}</td>
            <td>${app.district}</td>
            <td>${app.total_land_acres}</td>
            <td>${app.crop_type}</td>
            <td><span class="status-badge status-${app.status.toLowerCase()}">${app.status}</span></td>
            <td>${formatDate(app.submitted_date)}</td>
            <td>
                <button onclick='viewDetails(${JSON.stringify(app).replace(/'/g, "&apos;")})' class="btn-action btn-view" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Update statistics
function updateStatistics(applications) {
    const total = applications.length;
    const pending = applications.filter(app => app.status === 'Pending').length;
    const approved = applications.filter(app => app.status === 'Approved').length;
    const rejected = applications.filter(app => app.status === 'Rejected').length;
    
    document.getElementById('totalCount').textContent = total;
    document.getElementById('pendingCount').textContent = pending;
    document.getElementById('approvedCount').textContent = approved;
    document.getElementById('rejectedCount').textContent = rejected;
}

// Filter applications based on search and status
function filterApplications() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const statusFilter = document.getElementById('statusFilter').value;
    
    let filtered = allApplications;
    
    // Filter by status
    if (statusFilter) {
        filtered = filtered.filter(app => app.status === statusFilter);
    }
    
    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(app => 
            app.application_id.toLowerCase().includes(searchTerm) ||
            app.farmer_name.toLowerCase().includes(searchTerm) ||
            app.mobile_number.includes(searchTerm) ||
            app.aadhaar_number.includes(searchTerm) ||
            app.state.toLowerCase().includes(searchTerm) ||
            app.district.toLowerCase().includes(searchTerm)
        );
    }
    
    displayApplications(filtered);
}

// Refresh applications
function refreshApplications() {
    document.getElementById('historyTableBody').innerHTML = '<tr><td colspan="10" class="loading"><i class="fas fa-spinner fa-spin"></i> Refreshing...</td></tr>';
    loadApplications();
}

// View application details in modal
function viewDetails(application) {
    const modal = document.getElementById('detailsModal');
    const modalBody = document.getElementById('modalBody');
    
    modalBody.innerHTML = `
        <div class="details-grid">
            <div class="detail-item">
                <label><i class="fas fa-id-card"></i> Application ID</label>
                <p><strong>${application.application_id}</strong></p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-user"></i> Farmer Name</label>
                <p>${application.farmer_name}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-id-badge"></i> Aadhaar Number</label>
                <p>${application.aadhaar_number}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-phone"></i> Mobile Number</label>
                <p>${application.mobile_number}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-map-marker-alt"></i> State</label>
                <p>${application.state}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-map"></i> District</label>
                <p>${application.district}</p>
            </div>
            <div class="detail-item full-width">
                <label><i class="fas fa-home"></i> Address</label>
                <p>${application.address}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-chart-area"></i> Total Land (Acres)</label>
                <p>${application.total_land_acres}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-seedling"></i> Crop Type</label>
                <p>${application.crop_type}</p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-info-circle"></i> Status</label>
                <p><span class="status-badge status-${application.status.toLowerCase()}">${application.status}</span></p>
            </div>
            <div class="detail-item">
                <label><i class="fas fa-calendar"></i> Submitted Date</label>
                <p>${formatDate(application.submitted_date)}</p>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Close modal
function closeModal() {
    document.getElementById('detailsModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailsModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-IN', options);
}

// Show alert message
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
        alertContainer.innerHTML = '';
    }, 5000);
}
