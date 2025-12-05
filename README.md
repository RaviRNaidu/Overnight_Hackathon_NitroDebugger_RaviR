# 🌾 Farmer Portal - Government Agriculture Application System

A modern web-based portal for farmers to apply for fertilizers and subsidies, with department login for Agriculture officials and ML-based fraud detection.

## 🎯 Problem Statement

### Agricultural Input Subsidy Leakage Detection

**Context**: The Indian government spends over ₹70,000 crores annually on agricultural subsidies for fertilizers, seeds, and equipment through a network of dealers and cooperatives. However, a significant portion of these subsidies never reaches farmers. Dealers inflate beneficiary lists with ghost farmers, divert subsidized goods to the open market at higher prices, or create fake invoices for supplies never delivered.

**The Challenge**: Subsidy claims show unusual patterns like:
- Same dealer consistently serving unusually high numbers of farmers
- Beneficiaries receiving quantities exceeding their land holdings
- Geographically clustered claims suggesting coordinated fraud
- Ghost farmers making minimal repeated requests

**Why It Matters**: Subsidy leakage means farmers pay market prices while taxpayers fund phantom beneficiaries, undermining both agricultural productivity and government finances. Real farmers in remote areas miss out on crucial support during planting season while corrupt dealers profit.

## 🌾 Crop Norms & Eligibility System

### Overview
The system uses government-defined agricultural norms to validate subsidy requests and detect fraud. The `crop_norms.csv` file contains baseline data for 39+ Indian crops with standard fertilizer and seed requirements per acre.

**Location**: `backend/data/crop_norms.csv`

**Structure**:
```csv
crop,fertilizer_kg_per_acre,seed_kg_per_acre
Paddy,50,2
Wheat,45,2.5
Cotton,40,1
Sugarcane,60,3
```

### ⭐ USE CASE 1: Eligibility Engine (Foundation)

**Purpose**: Calculate maximum allowed subsidy quantity based on government norms.

**Formula**: 
```
allowed_qty = land_size_acres × rate_per_acre
```

**Example**:
- Farmer has 3 acres of Paddy
- Paddy fertilizer norm = 50 kg/acre
- **Allowed quantity** = 3 × 50 = **150 kg**

**How It Works**:
1. System loads `crop_norms.csv` into memory
2. When farmer enters Aadhaar, fetch their land size and crop type
3. Lookup crop norm from dataset
4. Calculate: `allowed_qty = land_size × rate_per_acre`
5. Return maximum allowed quantity

**No ML needed** - these are government-defined rules.

### ⭐ USE CASE 2: Real-Time Fraud Prevention

**Purpose**: Block fraudulent requests at submission time.

**Endpoint**: `POST /api/check-eligibility`

**Request**:
```json
{
  "crop_type": "Paddy",
  "land_size_acres": 3,
  "requested_qty": 200,
  "subsidy_type": "fertilizer"
}
```

**Response**:
```json
{
  "approved": false,
  "reason": "ABOVE_MAX_LIMIT",
  "risk_flag": "HIGH",
  "allowed_qty": 150,
  "requested_qty": 200,
  "qty_ratio": 1.333,
  "rate_per_acre": 50,
  "fraud_indicators": ["Requested 1.3x the allowed limit"]
}
```

**Fraud Prevention**:
- ✅ **Overclaiming**: Detects requests exceeding land capacity
- ✅ **Dealer fraud**: Prevents inflated subsidy requests
- ✅ **Ghost farmers**: Identifies suspiciously low requests (< 20% of norm)

**Decision Logic**:
```python
if requested_qty <= allowed_qty:
    → APPROVED
elif requested_qty <= allowed_qty × 1.1:  # 10% tolerance
    → APPROVED_WITH_TOLERANCE (LOW risk)
else:
    → REJECTED: ABOVE_MAX_LIMIT (HIGH risk)
```

### ⭐ USE CASE 3: ML-Based Fraud Detection

**Purpose**: Detect complex fraud patterns using machine learning.

**Algorithm**: Isolation Forest (unsupervised anomaly detection)

**Norm-Based Features** (engineered for ML):
```python
fertilizer_qty_ratio = requested_qty / (land_size × fertilizer_norm)
seed_qty_ratio = seed_requested / (land_size × seed_norm)
```

**Feature Analysis**:
- `qty_ratio > 1.0` → Overclaiming (requesting more than allowed)
- `qty_ratio < 0.2` repeatedly → Ghost farmer pattern (minimal requests)
- `qty_ratio` deviation from district average → Suspicious behavior

**ML Model Features**:
1. `land_acres` - Farm size
2. `expected_fertilizer_total` - Based on crop norms
3. `expected_seed_total` - Based on crop norms
4. `fertilizer_qty_ratio` - Requested / Expected (norm-based)
5. `seed_qty_ratio` - Requested / Expected (norm-based)
6. `district_application_density` - Geographic clustering
7. `land_deviation_from_district_avg` - Outlier detection
8. `state_application_count` - Regional patterns
9. `is_large_holding` - Unrealistic land sizes (> 100 acres)
10. `is_small_holding` - Suspiciously small holdings (< 0.5 acres)

**Fraud Patterns Detected**:
- 🚨 **Systematic overclaiming**: Dealers consistently requesting 1.5-2x norms
- 🚨 **Ghost farmers**: Repeated minimal requests (qty_ratio < 0.2)
- 🚨 **Coordinated fraud**: Clusters of similar ratio anomalies in same district
- 🚨 **Crop-specific fraud**: Exploiting high-subsidy crops (e.g., Banana, Cardamom)

**Endpoint**: `GET /api/fraud-analysis`

**Risk Scoring**:
- **HIGH** (anomaly_score > 0.6): Immediate verification required
- **MEDIUM** (0.4-0.6): Enhanced scrutiny
- **LOW** (0.2-0.4): Minor review
- **NORMAL** (< 0.2): Standard processing

### 🔍 How to Use Crop Norms

**Backend (Python)**:
```python
from fraud_detector import SubsidyFraudDetector

detector = SubsidyFraudDetector()

# USE CASE 1: Calculate allowed quantity
result = detector.calculate_allowed_quantity(
    crop_type="Paddy",
    land_size_acres=3,
    subsidy_type="fertilizer"
)
print(result)
# Output: {'allowed_qty': 150.0, 'rate_per_acre': 50, ...}

# USE CASE 2: Check eligibility (fraud prevention)
check = detector.check_eligibility(
    crop_type="Paddy",
    land_size_acres=3,
    requested_qty=200,
    subsidy_type="fertilizer"
)
print(check)
# Output: {'approved': False, 'reason': 'ABOVE_MAX_LIMIT', ...}
```

**Frontend (JavaScript)**:
```javascript
// USE CASE 2: Real-time validation before submission
async function validateSubsidyRequest(cropType, landSize, requestedQty) {
    const response = await fetch('http://localhost:8000/api/check-eligibility', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            crop_type: cropType,
            land_size_acres: parseFloat(landSize),
            requested_qty: parseFloat(requestedQty),
            subsidy_type: 'fertilizer'
        })
    });
    
    const result = await response.json();
    
    if (!result.approved) {
        alert(`Request denied: ${result.reason}\nAllowed: ${result.allowed_qty} kg\nRequested: ${result.requested_qty} kg`);
        return false;
    }
    
    return true;
}
```

### 📊 Crop Norms Dataset

**Included Crops** (39 total):
- **Food Grains**: Paddy, Wheat, Maize, Bajra, Jowar, Ragi, Barley
- **Pulses**: Arhar, Moong, Urad, Masur, Gram, Peas
- **Cash Crops**: Cotton, Sugarcane, Groundnut, Sunflower, Soybean, Mustard
- **Horticulture**: Banana, Mango, Orange, Grapes, Pomegranate, Papaya
- **Spices**: Turmeric, Chili, Ginger, Garlic, Coriander, Cumin
- **Plantation**: Tea, Coffee, Rubber, Coconut, Arecanut, Cardamom, Pepper

**Data Source**: Based on government agricultural department guidelines and regional farming practices.

## 📋 Project Structure

```
farmer-portal/
├── frontend/               # Frontend application
│   ├── index.html         # Department login page (landing page)
│   ├── dashboard.html     # Home dashboard
│   ├── application-form.html    # Farmer application form
│   ├── application-tracker.html # Track application status
│   ├── history.html       # Application history dashboard
│   ├── fraud-analysis.html # ML fraud detection dashboard
│   ├── auth.js           # Authentication guard
│   ├── styles.css         # Global styles
│   ├── app.js            # Application form logic
│   ├── tracker.js        # Tracker page logic
│   ├── login.js          # Login page logic
│   ├── history.js        # History dashboard logic
│   ├── fraud-analysis.js # Fraud detection UI logic
│   └── locations.js      # Indian states and districts data
│
└── backend/               # FastAPI backend
    ├── data/
    │   └── crop_norms.csv # Crop-wise subsidy norms
    ├── main.py           # Main API application
    ├── fraud_detector.py # ML fraud detection module
    ├── requirements.txt  # Python dependencies
    └── README.md         # Backend documentation
```

## ✨ Features

### 🔹 For Department Officials
- **Secure Login**: Department authentication required to access the portal
- **Application Form**: Submit farmer applications with all required details
- **Application Tracker**: Track application status using Application ID and Mobile Number
- **Application History**: View all applications with search, filter, and statistics
- **Fraud Analysis Dashboard**: ML-powered fraud detection with risk scoring
- **Eligibility Checking**: Real-time validation of subsidy requests
- **Session Management**: Automatic logout and session protection

### 🔹 ML Fraud Detection
- **Isolation Forest Algorithm**: Unsupervised anomaly detection
- **39+ Crop Norms**: Government-defined fertilizer and seed requirements
- **10 ML Features**: Including norm-based ratios, geographic clustering, land anomalies
- **4-Tier Risk Scoring**: HIGH, MEDIUM, LOW, NORMAL
- **Fraud Indicators**: Human-readable explanations for each flagged application
- **Real-Time Prevention**: Block fraudulent requests at submission time

### 🔹 UI/UX
- Clean, modern government portal theme
- Blue and white color scheme
- Responsive design for mobile and desktop
- Font Awesome icons
- Professional form validation
- Authentication-protected pages
- Risk-colored badges and indicators

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Backend Setup

1. Navigate to the backend folder:
```powershell
cd C:\Users\arunk\OneDrive\Desktop\farmer-portal\backend
```

2. Install Python dependencies:
```powershell
pip install -r requirements.txt
```

Dependencies include:
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- scikit-learn - ML algorithms
- pandas - Data processing
- numpy - Numerical computing
- joblib - Model serialization

3. Start the FastAPI server:
```powershell
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Frontend Setup

1. Navigate to the frontend folder:
```powershell
cd C:\Users\arunk\OneDrive\Desktop\farmer-portal\frontend
```

2. Open `index.html` in your web browser:
```powershell
Start-Process index.html
```

Or simply double-click `index.html` in File Explorer.

**Important**: You must login first to access any other pages in the portal.

## 🛠️ API Endpoints

### Applications
- `POST /api/applications` - Create new application
- `GET /api/applications/{id}?mobile_number={number}` - Get application by ID
- `GET /api/applications?department={dept}` - Get all applications
- `PUT /api/applications/{id}/status` - Update application status
- `DELETE /api/applications/{id}` - Delete application

### Fraud Detection & Eligibility
- `GET /api/fraud-analysis` - Get fraud statistics and flagged applications
- `GET /api/fraud-analysis/{application_id}` - Get fraud score for specific application
- `POST /api/train-fraud-model` - Train/retrain ML model (contamination parameter)
- `POST /api/check-eligibility` - Check if subsidy request is within allowed limits

### Authentication
- `POST /api/login` - Department user login

### Monitoring
- `GET /health` - Health check endpoint

## 🎨 Color Scheme

- **Primary Blue**: #1e3a8a (Navbar, headers)
- **Secondary Blue**: #3b82f6 (Buttons, accents)
- **Light Blue**: #dbeafe (Backgrounds)
- **Red**: #dc2626 (Logout button, HIGH risk)
- **Orange**: #f97316 (MEDIUM risk)
- **Yellow**: #eab308 (LOW risk)
- **Green**: #22c55e (NORMAL, approved)
- **White**: #ffffff
- **Gray Tones**: Various for text and borders

## 📦 Technologies Used

### Frontend
- HTML5
- CSS3 (with CSS Grid and Flexbox)
- Vanilla JavaScript (ES6+)
- Font Awesome 6.4.0 (Icons)
- Session Storage (Authentication)

### Backend
- FastAPI (Python web framework)
- Pydantic (Data validation)
- Uvicorn (ASGI server)

### Machine Learning
- scikit-learn (Isolation Forest)
- pandas (DataFrame operations)
- numpy (Numerical computations)
- joblib (Model serialization)

### Data
- crop_norms.csv (39 Indian crops with fertilizer/seed norms)
- In-memory database (applications_db, users_db)

## 🔒 Security Notes

**⚠️ Important for Production:**
- Replace in-memory storage with a proper database (PostgreSQL, MongoDB, etc.)
- Implement JWT-based authentication with token expiration
- Use environment variables for sensitive data
- Add rate limiting to prevent API abuse
- Implement HTTPS/TLS for secure communication
- Add input sanitization and SQL injection prevention
- Store crop norms in secure database instead of CSV

## 📱 Using the Portal

### Department Login (Required First)

1. Open the portal - you'll be directed to the **Login Page** automatically
2. Enter your User ID and Password
   - **Admin**: User ID: `admin` | Password: `admin123`
   - **Officer**: User ID: `officer1` | Password: `officer123`
3. Click **Login**
4. Upon successful login, you'll be redirected to the dashboard

### Submitting an Application

1. From the dashboard, navigate to **Application Form**
2. Fill in all required fields:
   - Farmer Name
   - Aadhaar Number (format: XXXX-XXXX-XXXX)
   - Mobile Number (10 digits)
   - State (select from dropdown)
   - District (select from dropdown - populated based on state)
   - Address
   - Total Land in Acres
   - Crop Type
3. Click **Submit Application**
4. Note down the Application ID provided

### Checking Subsidy Eligibility

**Via API**:
```bash
curl -X POST "http://localhost:8000/api/check-eligibility" \
     -H "Content-Type: application/json" \
     -d '{
       "crop_type": "Paddy",
       "land_size_acres": 5,
       "requested_qty": 300,
       "subsidy_type": "fertilizer"
     }'
```

**Expected Response**:
```json
{
  "approved": true,
  "reason": "APPROVED",
  "risk_flag": "NORMAL",
  "allowed_qty": 250,
  "requested_qty": 300,
  "qty_ratio": 1.2,
  "rate_per_acre": 50,
  "fraud_indicators": ["Requested 1.2x the allowed limit"]
}
```

### Tracking an Application

1. Navigate to **Application Tracker** from the navbar
2. Enter your Application ID
3. Enter your Mobile Number
4. Click **Track Application**
5. View your application status and details

### Viewing Application History

1. Navigate to **History** from the navbar
2. Search by Application ID or Farmer Name
3. Filter by status (Pending, Approved, Rejected)
4. View statistics (Total, Pending, Approved, Rejected)
5. Click "View Details" to see full application information

### Running Fraud Analysis

1. Navigate to **Fraud Analysis** from the navbar
2. Click **Train Model** to train on current applications (first time)
3. Click **Run Fraud Analysis** to analyze all applications
4. View statistics:
   - Total applications analyzed
   - Flagged anomalies count
   - HIGH / MEDIUM / LOW risk counts
5. Review flagged applications in the table
6. Click "View Details" for specific fraud indicators
7. Read recommendations for each risk level

### Logging Out

1. Click the **Logout** button in the navigation bar
2. You'll be redirected back to the login page

## 🧪 Testing the System

### Test Eligibility Checking

```python
# In Python terminal or script
from fraud_detector import SubsidyFraudDetector

detector = SubsidyFraudDetector()

# Normal request (should be approved)
result1 = detector.check_eligibility("Paddy", 5, 250, "fertilizer")
print(result1)  # approved: True, allowed: 250 kg

# Overclaiming request (should be rejected)
result2 = detector.check_eligibility("Paddy", 5, 400, "fertilizer")
print(result2)  # approved: False, ABOVE_MAX_LIMIT

# Ghost farmer pattern (suspiciously low)
result3 = detector.check_eligibility("Wheat", 10, 30, "fertilizer")
print(result3)  # approved: True, but has fraud_indicators
```

### Test ML Fraud Detection

```python
import pandas as pd

# Create test applications with anomalies
test_data = pd.DataFrame({
    'application_id': ['APP001', 'APP002', 'APP003', 'APP004'],
    'farmer_name': ['Normal Farmer', 'Ghost Farmer', 'Large Holder', 'Overclaimer'],
    'total_land_acres': [5, 0.3, 200, 10],
    'crop_type': ['Paddy', 'Wheat', 'Cotton', 'Sugarcane'],
    'district': ['District1', 'District1', 'District2', 'District1'],
    'state': ['State1', 'State1', 'State2', 'State1'],
    'fertilizer_qty': [250, 10, 500, 800],  # Some overclaiming
    'seed_qty': [10, 0.5, 100, 35]
})

# Train and analyze
detector.train(test_data, contamination=0.2)
results = detector.predict_anomalies(test_data)
print(results)
```

## 📚 Additional Resources

- **Backend README**: `backend/README.md` - Detailed API documentation
- **Setup Guide**: `SETUP-GUIDE.md` - Step-by-step installation
- **Quick Start**: `QUICKSTART.md` - Fast setup for developers
- **Authentication Guide**: `AUTHENTICATION-UPDATE.md` - Login system details

## 🤝 Support

For issues or questions:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the crop norms dataset at `backend/data/crop_norms.csv`
3. Check fraud detection module at `backend/fraud_detector.py`
4. Review ML model features and training in fraud analysis dashboard

## 📝 License

This is a government project for agricultural subsidy management and fraud detection.

---

**Developed for Government Agriculture Department**

**Fraud Detection powered by Machine Learning • Protecting ₹70,000+ crores in subsidies**
