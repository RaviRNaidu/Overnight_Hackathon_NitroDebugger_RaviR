// Application Tracker Handler
const API_URL = 'http://localhost:8002';

document.getElementById('trackerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const applicationId = document.getElementById('applicationId').value;
    const mobileNumber = document.getElementById('mobileNumber').value;

    try {
        const response = await fetch(`${API_URL}/api/applications/${applicationId}?mobile_number=${mobileNumber}`);
        const data = await response.json();

        if (response.ok) {
            displayResult(data);
        } else {
            showAlert('error', data.detail || 'Application not found');
            document.getElementById('trackerResult').style.display = 'none';
        }
    } catch (error) {
        showAlert('error', 'Network error. Please ensure the backend server is running.');
        document.getElementById('trackerResult').style.display = 'none';
    }
});

// Validate mobile number
document.getElementById('mobileNumber').addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
});

function displayResult(data) {
    document.getElementById('resultAppId').textContent = data.application_id;
    document.getElementById('resultFarmerName').textContent = data.farmer_name;
    
    const statusBadge = getStatusBadge(data.status);
    document.getElementById('resultStatus').innerHTML = statusBadge;
    
    document.getElementById('resultDepartment').textContent = 'Agriculture Department';
    
    document.getElementById('resultDate').textContent = formatDate(data.submitted_date);
    
    document.getElementById('trackerResult').style.display = 'block';
    
    showAlert('success', 'Application details retrieved successfully!');
}

function getStatusBadge(status) {
    const statusMap = {
        'approved': '<span class="status-badge status-approved"><i class="fas fa-check-circle"></i> Approved</span>',
        'pending': '<span class="status-badge status-pending"><i class="fas fa-clock"></i> Pending</span>',
        'rejected': '<span class="status-badge status-rejected"><i class="fas fa-times-circle"></i> Rejected</span>'
    };
    return statusMap[status.toLowerCase()] || status;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

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
