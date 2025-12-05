// Fraud Analysis Dashboard
const API_URL = 'http://localhost:8002';

let analysisResults = null;

// Run fraud analysis
async function runAnalysis() {
    try {
        showAlert('info', 'Running fraud analysis... Please wait.');
        
        const response = await fetch(`${API_URL}/api/fraud-analysis`);
        
        if (response.ok) {
            analysisResults = await response.json();
            displayResults(analysisResults);
            showAlert('success', 'Fraud analysis completed successfully!');
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Failed to run fraud analysis');
        }
    } catch (error) {
        showAlert('error', 'Network error. Please ensure the backend server is running.');
        console.error('Error:', error);
    }
}

// Display analysis results
function displayResults(results) {
    // Show sections
    document.getElementById('statsSection').style.display = 'block';
    document.getElementById('flaggedSection').style.display = 'block';
    
    // Update statistics
    const stats = results.statistics;
    document.getElementById('totalApps').textContent = stats.total_applications;
    document.getElementById('flaggedCount').textContent = stats.flagged_anomalies;
    document.getElementById('flaggedPercent').textContent = `${stats.anomaly_percentage}%`;
    document.getElementById('highRiskCount').textContent = stats.high_risk_count;
    document.getElementById('mediumRiskCount').textContent = stats.medium_risk_count;
    document.getElementById('lowRiskCount').textContent = stats.low_risk_count;
    
    // Display flagged applications
    displayFlaggedApplications(results.flagged_applications);
}

// Display flagged applications in table
function displayFlaggedApplications(applications) {
    const tbody = document.getElementById('fraudTableBody');
    
    if (!applications || applications.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="no-data">No high-risk applications detected</td></tr>';
        return;
    }
    
    tbody.innerHTML = applications.map(app => `
        <tr class="risk-${app.risk_level.toLowerCase()}">
            <td><strong>${app.application_id}</strong></td>
            <td>
                <span class="risk-badge risk-${app.risk_level.toLowerCase()}">
                    ${app.risk_level}
                </span>
            </td>
            <td>
                <span class="anomaly-score">${app.anomaly_score.toFixed(3)}</span>
            </td>
            <td>
                <ul class="indicators-list">
                    ${app.fraud_indicators.map(indicator => `
                        <li><i class="fas fa-exclamation-circle"></i> ${indicator}</li>
                    `).join('')}
                </ul>
            </td>
            <td>
                <button onclick="viewFraudDetails('${app.application_id}')" class="btn-action btn-view" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// View detailed fraud analysis for specific application
async function viewFraudDetails(applicationId) {
    try {
        const response = await fetch(`${API_URL}/api/fraud-analysis/${applicationId}`);
        
        if (response.ok) {
            const details = await response.json();
            showDetailModal(details);
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Failed to fetch fraud details');
        }
    } catch (error) {
        showAlert('error', 'Network error. Please ensure the backend server is running.');
        console.error('Error:', error);
    }
}

// Show fraud detail modal
function showDetailModal(details) {
    const modal = document.getElementById('detailModal');
    const modalBody = document.getElementById('modalDetailBody');
    
    const riskColor = {
        'HIGH': '#ef4444',
        'MEDIUM': '#f59e0b',
        'LOW': '#3b82f6',
        'NORMAL': '#10b981'
    }[details.risk_level];
    
    modalBody.innerHTML = `
        <div class="fraud-detail-grid">
            <div class="detail-card">
                <h3><i class="fas fa-id-card"></i> Application Information</h3>
                <p><strong>Application ID:</strong> ${details.application_id}</p>
                <p><strong>Risk Level:</strong> <span class="risk-badge risk-${details.risk_level.toLowerCase()}">${details.risk_level}</span></p>
                <p><strong>Anomaly Score:</strong> <span style="color: ${riskColor}; font-weight: bold;">${details.anomaly_score}</span></p>
                <p><strong>Flagged as Anomaly:</strong> ${details.is_anomaly ? '🚩 Yes' : '✅ No'}</p>
            </div>
            
            <div class="detail-card">
                <h3><i class="fas fa-chart-bar"></i> Statistical Details</h3>
                <p><strong>Land Size:</strong> ${details.details.land_acres} acres</p>
                <p><strong>District Application Density:</strong> ${details.details.district_density} applications</p>
                <p><strong>Land Deviation from Average:</strong> ±${details.details.land_deviation} acres</p>
            </div>
            
            <div class="detail-card full-width">
                <h3><i class="fas fa-flag"></i> Fraud Indicators</h3>
                <ul class="fraud-indicators-detail">
                    ${details.fraud_indicators.map(indicator => `
                        <li><i class="fas fa-exclamation-triangle"></i> ${indicator}</li>
                    `).join('')}
                </ul>
            </div>
            
            <div class="detail-card full-width">
                <h3><i class="fas fa-lightbulb"></i> Recommendation</h3>
                <p>${getRecommendation(details.risk_level)}</p>
            </div>
        </div>
    `;
    
    modal.style.display = 'block';
}

// Get recommendation based on risk level
function getRecommendation(riskLevel) {
    switch(riskLevel) {
        case 'HIGH':
            return '⚠️ <strong>Immediate Action Required:</strong> This application shows multiple red flags. Recommend thorough verification of farmer identity, land ownership documents, and physical inspection before approval.';
        case 'MEDIUM':
            return '⚡ <strong>Enhanced Scrutiny:</strong> This application has some unusual patterns. Recommend additional document verification and cross-checking with land records before processing.';
        case 'LOW':
            return 'ℹ️ <strong>Minor Review:</strong> Application shows slight deviations from norms. Standard verification process should be sufficient.';
        default:
            return '✅ <strong>Normal Processing:</strong> Application appears legitimate based on current analysis. Proceed with standard approval workflow.';
    }
}

// Close detail modal
function closeDetailModal() {
    document.getElementById('detailModal').style.display = 'none';
}

// Train fraud detection model
async function trainModel() {
    try {
        showAlert('info', 'Training fraud detection model... This may take a moment.');
        
        const response = await fetch(`${API_URL}/api/train-fraud-model`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const result = await response.json();
            showAlert('success', result.message);
            // Automatically run analysis after training
            setTimeout(runAnalysis, 1000);
        } else {
            const error = await response.json();
            showAlert('error', error.detail || 'Failed to train model');
        }
    } catch (error) {
        showAlert('error', 'Network error. Please ensure the backend server is running.');
        console.error('Error:', error);
    }
}

// Show alert message
function showAlert(type, message) {
    const alertContainer = document.getElementById('alertContainer');
    const alertClass = type === 'success' ? 'alert-success' : (type === 'info' ? 'alert-info' : 'alert-error');
    const icon = type === 'success' ? 'check-circle' : (type === 'info' ? 'info-circle' : 'exclamation-circle');
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            <i class="fas fa-${icon}"></i>
            ${message}
        </div>
    `;
    
    if (type !== 'info') {
        setTimeout(() => {
            alertContainer.innerHTML = '';
        }, 5000);
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Auto-run analysis on page load if applications exist
document.addEventListener('DOMContentLoaded', () => {
    // Optionally auto-run analysis
    // runAnalysis();
});
