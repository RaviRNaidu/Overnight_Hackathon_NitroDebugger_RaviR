// Application Form Handler
const API_URL = 'http://localhost:8002';

let aadhaarVerified = false;
let verifiedAadhaarData = null;

// Aadhaar verification
document.addEventListener('DOMContentLoaded', () => {
    const verifyBtn = document.getElementById('verifyAadhaarBtn');
    const aadhaarInput = document.getElementById('aadhaarNumber');

    if (verifyBtn && aadhaarInput) {
        verifyBtn.addEventListener('click', async () => {
            const aadhaar = aadhaarInput.value.replace(/-/g, '');
            
            if (aadhaar.length !== 12) {
                showAlert('Please enter a valid 12-digit Aadhaar number', 'error');
                return;
            }

            verifyBtn.disabled = true;
            verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

            try {
                const response = await fetch(`${API_URL}/api/aadhaar/search/${aadhaar}`);
                const data = await response.json();

                if (data.success && data.record) {
                    const record = data.record;
                    
                    // Check if person has land (acres > 0)
                    if (record.total_land_acres <= 0) {
                        showAlert('This Aadhaar holder has no registered land. Only farmers with land ownership can apply for subsidies.', 'error');
                        verifyBtn.disabled = false;
                        verifyBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify Aadhaar';
                        return;
                    }

                    // Store verified data
                    aadhaarVerified = true;
                    verifiedAadhaarData = record;

                    // Auto-fill form fields
                    document.getElementById('farmerName').value = record.name;
                    document.getElementById('mobileNumber').value = record.mobile_number;
                    document.getElementById('totalLandAcres').value = record.total_land_acres;
                    document.getElementById('state').value = record.state;
                    document.getElementById('district').value = record.district;
                    document.getElementById('address').value = record.address;

                    // Show verified details
                    document.getElementById('verifiedDetails').innerHTML = `
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; font-size: 14px;">
                            <div><strong>Name:</strong> ${record.name}</div>
                            <div><strong>Mobile:</strong> ${record.mobile_number}</div>
                            <div><strong>State:</strong> ${record.state}</div>
                            <div><strong>District:</strong> ${record.district}</div>
                            <div><strong>Total Land:</strong> ${record.total_land_acres} acres</div>
                            <div><strong>Village:</strong> ${record.village}</div>
                        </div>
                    `;

                    // Show status
                    const landStatus = document.getElementById('landStatus');
                    landStatus.textContent = `✓ Eligible to apply (${record.total_land_acres} acres registered)`;
                    landStatus.style.color = '#10b981';

                    // Show details section and crop section
                    document.getElementById('aadhaarDetailsSection').style.display = 'block';
                    document.getElementById('cropDetailsSection').style.display = 'block';

                    // Hide verify button and make aadhaar readonly
                    aadhaarInput.readOnly = true;
                    aadhaarInput.style.background = '#f3f4f6';
                    verifyBtn.style.display = 'none';
                    
                    // Scroll to crop section
                    setTimeout(() => {
                        document.getElementById('cropDetailsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 500);
                    
                    showAlert('✓ Aadhaar verified successfully! Please enter crop details below to calculate subsidies.', 'success');
                } else {
                    showAlert('Aadhaar number not found in database. Please ensure you are registered.', 'error');
                    verifyBtn.disabled = false;
                    verifyBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify Aadhaar';
                }
            } catch (error) {
                showAlert('Error verifying Aadhaar: ' + error.message, 'error');
                verifyBtn.disabled = false;
                verifyBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify Aadhaar';
            }
        });
    }

    // Populate State and District dropdowns (keeping for future use)
    const stateSelect = document.getElementById('state');
    const districtSelect = document.getElementById('district');

    if (window.INDIA_LOCATIONS && stateSelect && districtSelect) {
        // Fill states
        const states = Object.keys(window.INDIA_LOCATIONS);
        states.sort().forEach((state) => {
            const opt = document.createElement('option');
            opt.value = state;
            opt.textContent = state;
            stateSelect.appendChild(opt);
        });

        // On state change, fill districts
        stateSelect.addEventListener('change', () => {
            const selected = stateSelect.value;
            districtSelect.innerHTML = '';
            if (!selected) {
                const placeholder = document.createElement('option');
                placeholder.value = '';
                placeholder.textContent = '-- Select State First --';
                districtSelect.appendChild(placeholder);
                districtSelect.disabled = true;
                return;
            }
            const districts = window.INDIA_LOCATIONS[selected] || [];
            const placeholder = document.createElement('option');
            placeholder.value = '';
            placeholder.textContent = '-- Select District --';
            districtSelect.appendChild(placeholder);
            districts.forEach((d) => {
                const opt = document.createElement('option');
                opt.value = d;
                opt.textContent = d;
                districtSelect.appendChild(opt);
            });
            districtSelect.disabled = false;
        });

        // Initially disable district until a state is chosen
        districtSelect.disabled = true;
    }

    // Real-time eligibility checking
    const cropTypeInput = document.getElementById('cropType');
    const landAcresInput = document.getElementById('totalLandAcres');
    const fertilizerInput = document.getElementById('fertilizerQty');
    const seedInput = document.getElementById('seedQty');

    // Check eligibility and auto-set quantities when crop type and land size are entered
    async function checkEligibility() {
        const cropType = cropTypeInput?.value.trim();
        const landSize = parseFloat(landAcresInput?.value);

        if (!cropType || !landSize || landSize <= 0) {
            const section = document.getElementById('allowedQuantitiesSection');
            if (section) section.style.display = 'none';
            // Clear hidden field values
            if (fertilizerInput) fertilizerInput.value = '';
            if (seedInput) seedInput.value = '';
            return;
        }

        try {
            // Show loading
            const section = document.getElementById('allowedQuantitiesSection');
            if (section) {
                section.style.display = 'block';
                section.innerHTML = `
                    <h4 style="margin: 0; color: #1e3a8a;">
                        <i class="fas fa-spinner fa-spin"></i> Calculating subsidy quantities...
                    </h4>
                `;
            }

            // Check fertilizer eligibility
            const fertilizerResponse = await fetch(`${API_URL}/api/check-eligibility`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop_type: cropType,
                    land_size_acres: landSize,
                    requested_qty: 1,  // Dummy value to get allowed quantity
                    subsidy_type: 'fertilizer'
                })
            });

            const fertilizerData = await fertilizerResponse.json();

            // Check seed eligibility
            const seedResponse = await fetch(`${API_URL}/api/check-eligibility`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    crop_type: cropType,
                    land_size_acres: landSize,
                    requested_qty: 1,  // Dummy value to get allowed quantity
                    subsidy_type: 'seed'
                })
            });

            const seedData = await seedResponse.json();

            // Display allowed quantities and auto-set hidden field values
            if (fertilizerResponse.ok && seedResponse.ok && section) {
                // Display the calculated quantities
                section.innerHTML = `
                    <h4 style="margin: 0 0 15px 0; color: #1e3a8a;">
                        <i class="fas fa-check-circle"></i> Subsidy Quantities (Auto-calculated)
                    </h4>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Fertilizer Subsidy</label>
                            <input type="text" value="${fertilizerData.allowed_qty} kg (${fertilizerData.rate_per_acre} kg/acre × ${landSize} acres)" readonly style="background: #fff; font-weight: bold; color: #1e3a8a;">
                            <small style="color: #64748b;">Based on crop norms for ${cropType}</small>
                        </div>
                        <div class="form-group">
                            <label>Seed Subsidy</label>
                            <input type="text" value="${seedData.allowed_qty} kg (${seedData.rate_per_acre} kg/acre × ${landSize} acres)" readonly style="background: #fff; font-weight: bold; color: #1e3a8a;">
                            <small style="color: #64748b;">Based on crop norms for ${cropType}</small>
                        </div>
                    </div>
                `;

                // Auto-set the hidden field values to the allowed quantities
                if (fertilizerInput) fertilizerInput.value = fertilizerData.allowed_qty;
                if (seedInput) seedInput.value = seedData.allowed_qty;
                
                showAlert('✓ Subsidy quantities calculated! You can now submit the application.', 'success');
            } else if (section) {
                section.innerHTML = `
                    <h4 style="margin: 0; color: #dc2626;">
                        <i class="fas fa-exclamation-circle"></i> Unable to calculate subsidies
                    </h4>
                    <p style="margin: 10px 0 0 0; color: #64748b;">Please check crop type and try again.</p>
                `;
            }
        } catch (error) {
            console.error('Eligibility check failed:', error);
            const section = document.getElementById('allowedQuantitiesSection');
            if (section) {
                section.style.display = 'block';
                section.innerHTML = `
                    <h4 style="margin: 0; color: #dc2626;">
                        <i class="fas fa-exclamation-circle"></i> Error calculating subsidies
                    </h4>
                    <p style="margin: 10px 0 0 0; color: #64748b;">${error.message}</p>
                `;
            }
        }
    }

    // Trigger eligibility check when crop type or land size changes
    cropTypeInput?.addEventListener('blur', checkEligibility);
    cropTypeInput?.addEventListener('change', checkEligibility);
    cropTypeInput?.addEventListener('input', () => {
        // Debounce the input to avoid too many API calls
        clearTimeout(window.cropInputTimer);
        window.cropInputTimer = setTimeout(checkEligibility, 1000);
    });
    landAcresInput?.addEventListener('blur', checkEligibility);
    landAcresInput?.addEventListener('change', checkEligibility);
});

document.getElementById('applicationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Check if Aadhaar is verified
    if (!aadhaarVerified || !verifiedAadhaarData) {
        showAlert('Please verify your Aadhaar number first!', 'error');
        return;
    }

    // Check if land is > 0 (should always be true after verification, but double-check)
    if (verifiedAadhaarData.total_land_acres <= 0) {
        showAlert('Only farmers with registered land can submit applications.', 'error');
        return;
    }
    
    const formData = {
        farmer_name: document.getElementById('farmerName').value,
        aadhaar_number: document.getElementById('aadhaarNumber').value,
        mobile_number: document.getElementById('mobileNumber').value,
        state: document.getElementById('state').value,
        district: document.getElementById('district').value,
        address: document.getElementById('address').value,
        total_land_acres: parseFloat(document.getElementById('totalLandAcres').value),
        crop_type: document.getElementById('cropType').value,
        fertilizer_qty: parseFloat(document.getElementById('fertilizerQty').value),
        seed_qty: parseFloat(document.getElementById('seedQty').value)
    };

    try {
        // Submit application directly (quantities are auto-calculated to allowed amounts)
        showLoadingMessage('Submitting application...');
        
        const response = await fetch(`${API_URL}/api/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        hideLoadingMessage();

        if (response.ok) {
            // Show success message with notification info
            const successMessage = `
                Application submitted successfully! 
                
                Application ID: ${data.application_id}
                
                ðŸ“± An SMS notification with your subsidy details has been sent to ${formData.mobile_number}.
                
                Details:
                â€¢ Fertilizer Subsidy: ${formData.fertilizer_qty} kg
                â€¢ Seed Subsidy: ${formData.seed_qty} kg
            `.trim();
            
            showAlert(successMessage, 'success');
            
            // Reset form and state
            document.getElementById('applicationForm').reset();
            document.getElementById('allowedQuantitiesSection').style.display = 'none';
            document.getElementById('aadhaarDetailsSection').style.display = 'none';
            document.getElementById('cropDetailsSection').style.display = 'none';
            document.getElementById('verifyAadhaarBtn').style.display = 'block';
            document.getElementById('aadhaarNumber').readOnly = false;
            document.getElementById('aadhaarNumber').style.background = '';
            aadhaarVerified = false;
            verifiedAadhaarData = null;
        } else {
            // Handle validation errors
            let errorMessage = 'Failed to submit application';
            if (data.detail) {
                if (Array.isArray(data.detail)) {
                    errorMessage = data.detail.map(err => `${err.loc.join('.')}: ${err.msg}`).join(', ');
                } else if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                } else {
                    errorMessage = JSON.stringify(data.detail);
                }
            }
            showAlert(errorMessage, 'error');
        }
    } catch (error) {
        hideLoadingMessage();
        showAlert(`Network error: ${error.message}. Please ensure the backend server is running.`, 'error');
    }
});

// Auto-format Aadhaar number
document.getElementById('aadhaarNumber').addEventListener('input', (e) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length > 12) value = value.slice(0, 12);
    
    const parts = [];
    for (let i = 0; i < value.length; i += 4) {
        parts.push(value.slice(i, i + 4));
    }
    e.target.value = parts.join('-');
});

// Validate mobile number
document.getElementById('mobileNumber').addEventListener('input', (e) => {
    e.target.value = e.target.value.replace(/\D/g, '').slice(0, 10);
});

function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    const alertClass = type === 'success' ? 'alert-success' : (type === 'error' ? 'alert-error' : 'alert-info');
    
    alertContainer.innerHTML = `
        <div class="alert ${alertClass}">
            <i class="fas fa-${type === 'success' ? 'check-circle' : (type === 'error' ? 'exclamation-circle' : 'info-circle')}"></i>
            ${message}
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        alertContainer.innerHTML = '';
    }, 5000);
}

function showLoadingMessage(message) {
    const alertContainer = document.getElementById('alertContainer');
    alertContainer.innerHTML = `
        <div class="alert" style="background: #dbeafe; color: #1e3a8a; border-left: 4px solid #3b82f6;">
            <i class="fas fa-spinner fa-spin"></i>
            ${message}
        </div>
    `;
}

function hideLoadingMessage() {
    document.getElementById('alertContainer').innerHTML = '';
}

async function showFraudPrediction(fraudCheck, formData) {
    return new Promise((resolve) => {
        const riskLevel = fraudCheck.risk_flag || 'NORMAL';
        const qtyRatio = fraudCheck.qty_ratio || 1.0;
        const allowedQty = fraudCheck.allowed_qty || 0;
        const requestedQty = fraudCheck.requested_qty || 0;
        
        // Determine colors and icons based on risk
        let bgColor, textColor, icon, title, recommendation;
        
        if (riskLevel === 'HIGH') {
            bgColor = '#fef2f2';
            textColor = '#dc2626';
            icon = 'fa-exclamation-triangle';
            title = 'ðŸš¨ HIGH RISK DETECTED';
            recommendation = 'This application shows signs of potential fraud. Please verify all details carefully before proceeding.';
        } else if (riskLevel === 'MEDIUM') {
            bgColor = '#fff7ed';
            textColor = '#f97316';
            icon = 'fa-exclamation-circle';
            title = 'âš ï¸ MEDIUM RISK DETECTED';
            recommendation = 'This application requires enhanced scrutiny. Review the quantities requested.';
        } else if (riskLevel === 'LOW') {
            bgColor = '#fefce8';
            textColor = '#eab308';
            icon = 'fa-info-circle';
            title = 'ðŸ’¡ LOW RISK DETECTED';
            recommendation = 'Minor review recommended before approval.';
        } else {
            bgColor = '#f0fdf4';
            textColor = '#22c55e';
            icon = 'fa-check-circle';
            title = 'âœ… NORMAL - No Fraud Detected';
            recommendation = 'Application appears legitimate and within expected parameters.';
        }

        // Create modal overlay
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        // Create modal content
        const modalContent = document.createElement('div');
        modalContent.style.cssText = `
            background: white;
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
        `;

        const fraudIndicators = fraudCheck.fraud_indicators || [];
        const indicatorsHTML = fraudIndicators && fraudIndicators.length > 0 
            ? `<div style="margin: 15px 0;">
                <strong style="color: #64748b;">Fraud Indicators:</strong>
                <ul style="margin: 10px 0; padding-left: 20px; color: #64748b;">
                    ${fraudIndicators.map(ind => `<li>${ind}</li>`).join('')}
                </ul>
               </div>`
            : '';

        modalContent.innerHTML = `
            <div style="background: ${bgColor}; padding: 20px; border-radius: 12px 12px 0 0;">
                <h3 style="margin: 0; color: ${textColor}; display: flex; align-items: center; gap: 10px;">
                    <i class="fas ${icon}"></i>
                    ${title}
                </h3>
            </div>
            
            <div style="padding: 25px;">
                <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <small style="color: #64748b; display: block; margin-bottom: 5px;">Farmer Name</small>
                            <strong>${formData.farmer_name}</strong>
                        </div>
                        <div>
                            <small style="color: #64748b; display: block; margin-bottom: 5px;">Crop Type</small>
                            <strong>${formData.crop_type}</strong>
                        </div>
                        <div>
                            <small style="color: #64748b; display: block; margin-bottom: 5px;">Land Size</small>
                            <strong>${formData.total_land_acres} acres</strong>
                        </div>
                        <div>
                            <small style="color: #64748b; display: block; margin-bottom: 5px;">Risk Level</small>
                            <strong style="color: ${textColor};">${riskLevel}</strong>
                        </div>
                    </div>
                </div>

                <div style="background: #fff7ed; border-left: 4px solid #f97316; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
                    <div style="margin-bottom: 10px;">
                        <strong style="color: #1e3a8a;">Subsidy Analysis:</strong>
                    </div>
                    <div style="display: grid; gap: 10px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span>Allowed Fertilizer:</span>
                            <strong style="color: #22c55e;">${allowedQty} kg</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Requested Fertilizer:</span>
                            <strong style="color: ${requestedQty > allowedQty ? '#dc2626' : '#1e3a8a'};">${requestedQty} kg</strong>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Quantity Ratio:</span>
                            <strong style="color: ${qtyRatio > 1 ? '#dc2626' : '#22c55e'};">${qtyRatio.toFixed(2)}x</strong>
                        </div>
                    </div>
                </div>

                ${indicatorsHTML}

                <div style="background: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid ${textColor};">
                    <strong style="color: #1e3a8a; display: block; margin-bottom: 8px;">
                        <i class="fas fa-lightbulb"></i> Recommendation:
                    </strong>
                    <p style="margin: 0; color: #64748b; line-height: 1.6;">
                        ${recommendation}
                    </p>
                </div>

                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button id="cancelSubmit" style="
                        padding: 12px 24px;
                        background: #f1f5f9;
                        border: 1px solid #cbd5e1;
                        border-radius: 8px;
                        color: #475569;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                    ">
                        <i class="fas fa-times"></i> Cancel
                    </button>
                    <button id="confirmSubmit" style="
                        padding: 12px 24px;
                        background: #3b82f6;
                        border: none;
                        border-radius: 8px;
                        color: white;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                    ">
                        <i class="fas fa-check"></i> Proceed Anyway
                    </button>
                </div>
            </div>
        `;

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Add hover effects
        const cancelBtn = modal.querySelector('#cancelSubmit');
        const confirmBtn = modal.querySelector('#confirmSubmit');
        
        cancelBtn.addEventListener('mouseenter', () => {
            cancelBtn.style.background = '#e2e8f0';
        });
        cancelBtn.addEventListener('mouseleave', () => {
            cancelBtn.style.background = '#f1f5f9';
        });
        
        confirmBtn.addEventListener('mouseenter', () => {
            confirmBtn.style.background = '#2563eb';
        });
        confirmBtn.addEventListener('mouseleave', () => {
            confirmBtn.style.background = '#3b82f6';
        });

        // Handle button clicks
        cancelBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
            resolve(false);
        });

        confirmBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
            resolve(true);
        });

        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
                resolve(false);
            }
        });
    });
}

