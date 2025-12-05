# 📝 Application Form - Fertilizer & Seed Quantity Fields Guide

## 🎯 What's New in the Form

The farmer application form now captures **actual requested quantities** for fertilizer and seed, enabling:
- ✅ Real-time eligibility checking against crop norms
- ✅ Fraud detection using norm-based ratio analysis
- ✅ Automatic calculation of allowed quantities
- ✅ Instant validation with visual warnings

---

## 📋 Complete Form Fields

### Section 1: Farmer Details
1. **Farmer Name** * (text)
2. **Aadhaar Number** * (XXXX-XXXX-XXXX format)
3. **Mobile Number** * (10 digits)

### Section 2: Location
4. **State** * (dropdown)
5. **District** * (dropdown - auto-populated based on state)
6. **Address** * (textarea)

### Section 3: Land & Crop Information
7. **Total Land (Acres)** * (number, min: 0, step: 0.01)
8. **Crop Type** * (text, e.g., Paddy, Wheat, Cotton)

### Section 4: 📊 Allowed Quantities (Auto-Calculated) ⭐ NEW
**This section appears automatically when Crop Type and Land Size are entered**

**Blue Info Box Displays:**
```
📊 Allowed Subsidy Quantities (Based on Crop Norms)

┌─────────────────────────────────────────────────┐
│ Fertilizer Allowance                            │
│ 250 kg (50 kg/acre × 5 acres)                   │
│ Maximum fertilizer based on your land and crop  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Seed Allowance                                  │
│ 10 kg (2 kg/acre × 5 acres)                     │
│ Maximum seed based on your land and crop        │
└─────────────────────────────────────────────────┘
```

### Section 5: Requested Quantities ⭐ NEW
9. **Requested Fertilizer Quantity (kg)** * (number, min: 0, step: 0.1)
   - Real-time validation against allowed fertilizer
   - ⚠️ Red warning if exceeds allowed limit
   
10. **Requested Seed Quantity (kg)** * (number, min: 0, step: 0.1)
    - Real-time validation against allowed seed
    - ⚠️ Red warning if exceeds allowed limit

---

## 🎬 User Experience Flow

### Example: Farmer Growing Paddy on 5 Acres

**Step 1:** Fill in basic details
```
Farmer Name: Rajesh Kumar
Aadhaar: 1234-5678-9012
Mobile: 9876543210
State: Tamil Nadu
District: Thanjavur
Address: Village Kumbakonam, 612001
```

**Step 2:** Enter land and crop
```
Total Land (Acres): 5
Crop Type: Paddy  👈 User types and tabs out
```

**Step 3:** 🔄 **System Auto-Calculates** (happens in background)
```javascript
// Backend API Call
POST /api/check-eligibility
{
  "crop_type": "Paddy",
  "land_size_acres": 5,
  "subsidy_type": "fertilizer"
}

// Response
{
  "allowed_qty": 250,
  "rate_per_acre": 50
}
```

**Step 4:** 📊 **Blue Box Appears**
```
┌──────────────────────────────────────────────┐
│ 📊 Allowed Subsidy Quantities                │
│                                              │
│ Fertilizer Allowance                         │
│ [250 kg (50 kg/acre × 5 acres)]             │
│ Maximum fertilizer based on your land        │
│                                              │
│ Seed Allowance                               │
│ [10 kg (2 kg/acre × 5 acres)]               │
│ Maximum seed based on your land              │
└──────────────────────────────────────────────┘
```

**Step 5:** Farmer enters requested quantities

**Scenario A: Normal Request ✅**
```
Requested Fertilizer Quantity (kg): 240
Requested Seed Quantity (kg): 9

✅ No warning (within limits)
✅ Green border on inputs
```

**Scenario B: Overclaiming ⚠️**
```
Requested Fertilizer Quantity (kg): 350  👈 Exceeds 250 kg allowed

⚠️ Warning appears: "Exceeds allowed limit!"
🔴 Input border turns red
💡 Farmer sees they requested 350 but only 250 is allowed
```

**Scenario C: Ghost Farmer Pattern 🚨**
```
Requested Fertilizer Quantity (kg): 30   👈 Only 30 kg for 5 acres?
Requested Seed Quantity (kg): 1          👈 Suspiciously low

⚠️ System flags: "Suspiciously low request (possible ghost farmer pattern)"
📊 Ratio = 30/250 = 0.12 (< 0.2 threshold)
```

**Step 6:** Submit form
```
✅ Data sent to backend:
{
  "farmer_name": "Rajesh Kumar",
  "total_land_acres": 5,
  "crop_type": "Paddy",
  "fertilizer_qty": 240,  ⭐ NEW
  "seed_qty": 9,          ⭐ NEW
  ...
}
```

---

## 🔍 What Happens Behind the Scenes

### 1. Real-Time Eligibility Check
```javascript
// app.js - Triggered when crop type or land size changes
async function checkEligibility() {
  // Get crop norms from backend
  const response = await fetch('/api/check-eligibility', {
    method: 'POST',
    body: JSON.stringify({
      crop_type: cropType,
      land_size_acres: landSize,
      requested_qty: 1,  // Dummy value
      subsidy_type: 'fertilizer'
    })
  });
  
  // Display allowed quantities
  allowedFertilizer.value = `${data.allowed_qty} kg`;
}
```

### 2. Validation on Input
```javascript
// app.js - Triggered when farmer types quantity
function validateQuantity(inputElement) {
  const requested = parseFloat(inputElement.value);
  const allowed = parseFloat(inputElement.dataset.allowedQty);
  
  if (requested > allowed) {
    // Show warning
    warningElement.style.display = 'block';
    inputElement.style.borderColor = '#dc2626';
  }
}
```

### 3. Backend Storage
```python
# main.py - Application stored with new fields
applications_db[app_id] = {
    "application_id": app_id,
    "farmer_name": application.farmer_name,
    "total_land_acres": application.total_land_acres,
    "crop_type": application.crop_type,
    "fertilizer_qty": application.fertilizer_qty,  # NEW
    "seed_qty": application.seed_qty,              # NEW
    "status": "Pending",
    "submitted_date": datetime.now()
}
```

### 4. ML Fraud Detection
```python
# fraud_detector.py - Analyzes submitted data
def extract_features(applications_df):
    norms = get_crop_norm(app['crop_type'])
    expected_fertilizer = norms['fertilizer_per_acre'] * app['total_land_acres']
    
    # Calculate ratio features
    fertilizer_ratio = app['fertilizer_qty'] / expected_fertilizer
    # ratio > 1.5  → HIGH RISK
    # ratio > 1.0  → OVERCLAIMING
    # ratio < 0.2  → GHOST FARMER
```

---

## 📊 Crop Norms Used for Calculations

| Crop        | Fertilizer (kg/acre) | Seed (kg/acre) | Example: 5 Acres         |
|-------------|---------------------|----------------|--------------------------|
| Paddy       | 50                  | 2              | 250 kg, 10 kg            |
| Wheat       | 45                  | 2.5            | 225 kg, 12.5 kg          |
| Cotton      | 40                  | 1              | 200 kg, 5 kg             |
| Sugarcane   | 60                  | 3              | 300 kg, 15 kg            |
| Maize       | 48                  | 2.2            | 240 kg, 11 kg            |
| Banana      | 70                  | 5              | 350 kg, 25 kg            |
| Tea         | 45                  | 2              | 225 kg, 10 kg            |
| Coffee      | 40                  | 1.5            | 200 kg, 7.5 kg           |

**Source**: `backend/data/crop_norms.csv` (39 crops total)

---

## 🚨 Fraud Detection Patterns

### Pattern 1: Systematic Overclaiming
```
Farmer A - Paddy, 5 acres:
  Allowed: 250 kg fertilizer
  Requested: 375 kg
  Ratio: 1.5 (50% over)
  Status: 🚨 HIGH RISK

Action: Flag for immediate verification
```

### Pattern 2: Ghost Farmer
```
Farmer B - Wheat, 10 acres:
  Allowed: 450 kg fertilizer
  Requested: 50 kg
  Ratio: 0.11 (89% under)
  Status: 🚨 SUSPICIOUS (Ghost farmer pattern)

Action: Verify farmer identity and land ownership
```

### Pattern 3: Coordinated Fraud
```
District: Thanjavur
Pattern: 15 farmers, all requesting exactly 1.5x allowed
Analysis: Geographic clustering + identical ratios
Status: 🚨 COORDINATED FRAUD RING

Action: District-level investigation
```

### Pattern 4: Normal Usage
```
Farmer C - Cotton, 8 acres:
  Allowed: 320 kg fertilizer
  Requested: 300 kg
  Ratio: 0.94 (within normal range)
  Status: ✅ NORMAL

Action: Standard processing
```

---

## 🎨 Visual Indicators

### Input Field States

**Normal State (No Input Yet)**
```css
border: 1px solid #d1d5db;
background: white;
```

**Valid Input ✅**
```css
border: 1px solid #d1d5db;
background: white;
/* No warning shown */
```

**Exceeds Limit ⚠️**
```css
border: 2px solid #dc2626;  /* Red border */
background: #fef2f2;         /* Light red background */
```

**Warning Message**
```html
<small style="color: #dc2626;">
  <i class="fas fa-exclamation-triangle"></i> 
  Exceeds allowed limit!
</small>
```

### Allowed Quantities Box
```css
background: #dbeafe;         /* Light blue */
border-radius: 8px;
padding: 15px;
color: #1e3a8a;              /* Dark blue text */
font-weight: bold;
```

---

## 🧪 Test Cases

### Test Case 1: Normal Paddy Farmer
```
Input:
  Land: 5 acres
  Crop: Paddy
  Fertilizer: 240 kg
  Seed: 9 kg

Expected:
  ✅ Allowed fertilizer: 250 kg displayed
  ✅ Allowed seed: 10 kg displayed
  ✅ No warnings
  ✅ Form submits successfully
```

### Test Case 2: Overclaiming
```
Input:
  Land: 3 acres
  Crop: Wheat
  Fertilizer: 200 kg (allowed: 135 kg)
  Seed: 10 kg (allowed: 7.5 kg)

Expected:
  ⚠️ Red warning on fertilizer: "Exceeds allowed limit!"
  ⚠️ Red warning on seed: "Exceeds allowed limit!"
  ⚠️ Red borders on both inputs
  ℹ️ Form can still submit (backend will flag for review)
```

### Test Case 3: Ghost Farmer
```
Input:
  Land: 20 acres (large holding)
  Crop: Cotton
  Fertilizer: 50 kg (allowed: 800 kg)
  Seed: 2 kg (allowed: 20 kg)

Expected:
  ✅ No frontend warning (under limit)
  🚨 Backend ML flags: ratio = 0.06 (< 0.2)
  🚨 Fraud indicators: "Suspiciously low request"
```

---

## 📱 Responsive Design

### Desktop View (> 768px)
```
┌────────────────────────────────────────────────────────┐
│  Fertilizer Qty    │  Seed Qty                         │
│  [  240 kg  ]      │  [  9 kg  ]                       │
└────────────────────────────────────────────────────────┘
```

### Mobile View (< 768px)
```
┌──────────────────────┐
│  Fertilizer Qty      │
│  [  240 kg  ]        │
└──────────────────────┘
┌──────────────────────┐
│  Seed Qty            │
│  [  9 kg  ]          │
└──────────────────────┘
```

---

## 🔗 API Integration

### Frontend → Backend
```javascript
// Form submission with new fields
const formData = {
  farmer_name: "Rajesh Kumar",
  total_land_acres: 5,
  crop_type: "Paddy",
  fertilizer_qty: 240,  // ⭐ NEW
  seed_qty: 9,          // ⭐ NEW
  ...
};

fetch('/api/applications', {
  method: 'POST',
  body: JSON.stringify(formData)
});
```

### Backend → ML Model
```python
# Applications stored in database
apps_df = pd.DataFrame(applications_db.values())

# ML model extracts features
features = fraud_detector.extract_features(apps_df)
# Now includes: fertilizer_qty_ratio, seed_qty_ratio

# Predict anomalies
results = fraud_detector.predict_anomalies(apps_df)
```

---

## 🎓 Summary

**Before**: Form only captured land size and crop type
**After**: Form captures actual requested quantities with real-time validation

**Benefits**:
1. ✅ Farmers see allowed limits before requesting
2. ✅ Prevents accidental overclaiming
3. ✅ Detects intentional fraud (ratio > 1.5)
4. ✅ Identifies ghost farmers (ratio < 0.2)
5. ✅ ML model has richer data (10 features vs 7)
6. ✅ Real-time feedback improves user experience

**ML Enhancement**:
- Old: Only geographic and land-based features
- New: Norm-based ratio analysis (fertilizer_qty_ratio, seed_qty_ratio)
- Impact: Detects overclaiming, ghost farmers, and coordinated fraud

---

**Ready to use! Start the backend and test the enhanced form.**

```bash
cd backend
python main.py
# Open frontend/application-form.html in browser
```
