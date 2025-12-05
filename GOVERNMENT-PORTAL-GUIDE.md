# Government Portal - User Guide

## 🏛️ Government Portal Overview

The Government Portal allows agriculture department officers to review, manage, and approve/reject farmer subsidy applications with ML-powered fraud detection insights.

## ✨ Features

### 1. **Dashboard Statistics**
- Pending Review count
- Under Review count
- Approved applications
- Rejected applications
- High Risk applications

### 2. **Application Review**
- View all applications in a table format
- See ML fraud risk scores for each application
- Filter by status, risk level, state, district
- Search by farmer name, application ID, or Aadhaar number

### 3. **ML Integration**
- Real-time fraud detection using Hackathon_Nitro models
- Risk levels: LOW, MEDIUM, HIGH
- Fraud warnings and alerts
- Detailed analysis metrics

### 4. **Application Management**
- View complete application details
- See ML fraud analysis
- Add review comments
- Approve/Reject applications
- Mark applications under review

## 🚀 How to Use

### Starting the System

1. **Start Backend Server:**
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Open Government Portal:**
Open `frontend/government-portal.html` in your web browser

### Reviewing Applications

#### Step 1: View Applications List
- The dashboard shows all applications with their current status
- Applications are automatically enriched with ML fraud predictions
- Color-coded risk badges: Green (LOW), Yellow (MEDIUM), Red (HIGH)

#### Step 2: Filter Applications
Use filters to find specific applications:
- **Status:** pending, under_review, approved, rejected
- **Risk Level:** LOW, MEDIUM, HIGH
- **State/District:** Filter by location
- **Search:** Search by name, ID, or Aadhaar

#### Step 3: View Application Details
Click on any application row or "View" button to see:
- **Farmer Information:** Name, Aadhaar, mobile, address
- **Land Details:** Total land, crop type
- **Request Details:** Fertilizer qty, seed qty
- **ML Analysis:** Fraud score, risk level, warnings
- **Analysis Details:** Quantity per hectare, subsidy amount, etc.

#### Step 4: Review and Decision
For pending or under-review applications:

**To Approve:**
1. Click "View" on the application
2. Enter review comments (required)
3. Click "✓ Approve"
4. Application status changes to "approved"

**To Reject:**
1. Click "View" on the application
2. Enter review comments (required)
3. Click "✗ Reject"
4. Application status changes to "rejected"

**To Mark Under Review:**
1. Click "View" on pending application
2. Optionally enter comments
3. Click "📝 Mark Under Review"
4. Application status changes to "under_review"

## 📊 Understanding ML Analysis

### Fraud Score
- **0-40%:** Low risk - Safe to approve
- **40-70%:** Medium risk - Review recommended
- **70-100%:** High risk - Manual verification required

### Risk Levels
- **LOW:** Normal application, no suspicious patterns
- **MEDIUM:** Some concerns, review recommended
- **HIGH:** Multiple red flags, manual verification needed

### Warnings
The ML system generates warnings for:
- Unusually high quantity per hectare
- Requested quantity exceeds scheme limits
- Transaction at unusual hours
- Large distance between farmer and dealer

### Analysis Details
- **Quantity per hectare:** Should be reasonable (< 200 kg/ha)
- **Quantity vs Allowed:** Should be < 1.2 (within 120% of allowed)
- **Subsidy Amount:** Calculated based on quantity
- **Claimed Land:** In hectares

## 🔐 Application Status Flow

```
Pending → Under Review → Approved/Rejected
   ↓                            ↑
   └────────────────────────────┘
```

- **Pending:** Newly submitted, awaiting review
- **Under Review:** Being reviewed by officer
- **Approved:** Accepted for subsidy processing
- **Rejected:** Denied with comments

## 📱 API Endpoints Used

### Get All Applications
```
GET /api/applications
Returns: List of all applications with review fields
```

### Update Application Status
```
PUT /api/applications/{application_id}/status
Body: {
  "status": "approved|rejected|under_review",
  "review_comments": "Your comments",
  "reviewed_by": "Officer Name"
}
```

### ML Fraud Prediction
```
POST /api/ml/predict-fraud
Body: Application data
Returns: Fraud score, risk level, warnings
```

## 💡 Best Practices

### For Low Risk Applications (< 40%)
- Quick approval possible
- Review basic details
- Minimal comments required

### For Medium Risk Applications (40-70%)
- Thorough review recommended
- Check land vs quantity ratio
- Verify farmer details
- Provide detailed comments

### For High Risk Applications (> 70%)
- Mandatory manual verification
- Check all warnings
- Verify with field officer
- Consider rejection or request more documents
- Detailed comments essential

## 🎯 Keyboard Shortcuts

- **Click Row:** View application details
- **ESC:** Close modal
- **Enter in Search:** Apply filters

## 📈 Statistics Tracking

The dashboard automatically tracks:
- Total pending applications
- Applications under review
- Total approved applications
- Total rejected applications
- High-risk applications requiring attention

## ⚠️ Important Notes

1. **Review Comments:** Required for approve/reject decisions
2. **ML Scores:** Use as guidance, not sole decision factor
3. **Warnings:** Investigate thoroughly before approval
4. **Status Updates:** Permanent once saved
5. **Audit Trail:** Reviewer name and time are recorded

## 🔄 Real-time Updates

- Applications list refreshes after status changes
- Statistics update automatically
- ML predictions cached for performance
- Filters apply instantly

## 📞 Support

For issues or questions:
- Check ML Integration documentation
- Review API documentation at http://localhost:8000/docs
- Verify database connectivity
- Check backend logs for errors

## 🎓 Training Tips

1. Start with low-risk applications to familiarize yourself
2. Review ML warnings to understand patterns
3. Compare similar applications for consistency
4. Use filters to prioritize high-risk cases
5. Maintain detailed review comments for records

---

**Version:** 1.0.0  
**Last Updated:** December 5, 2025  
**System:** Farmer Portal - Government Review Portal
