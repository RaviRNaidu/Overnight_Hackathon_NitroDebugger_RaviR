# Government Portal Login Credentials

## Access Information

The Government Portal is a secure admin interface for reviewing and managing farmer subsidy applications with ML-powered fraud detection.

### Login Credentials

#### Government Administrator
- **Username:** `gov_admin`
- **Password:** `gov@123`
- **Role:** Full administrative access

#### Government Review Officer
- **Username:** `gov_officer`
- **Password:** `gov@456`
- **Role:** Application review and approval

#### Agriculture Department (Legacy Access)
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Agriculture admin

- **Username:** `officer1`
- **Password:** `officer123`
- **Role:** Agriculture officer

---

## How to Access

1. **Navigate to Login Page**
   - Open `frontend/index.html` in your browser
   - Or visit the home page of the application

2. **Enter Credentials**
   - Use any of the government portal credentials above
   - Click "Login"

3. **Access Government Portal**
   - Click on "Government Portal" in the navigation menu
   - Or directly open `frontend/government-portal.html`

---

## Portal Features

### 📊 Dashboard
- Real-time statistics (Pending, Under Review, Approved, Rejected, Risk Flagged)
- Quick overview of all applications

### 🔍 Filters
- **Status:** Pending, Under Review, Approved, Rejected
- **Risk Level:** Safe (✓) or Risk (⚠️)
- **Location:** Filter by State and District
- **Search:** By farmer name, Aadhaar, or Application ID

### 🤖 ML Integration
- Automatic fraud detection for each application
- Binary risk classification (SAFE/RISK)
- Detailed fraud analysis with warnings
- Real-time fraud score calculation

### ✅ Review Workflow
1. View application details
2. Review ML fraud analysis
3. Add review comments
4. Approve, Reject, or Mark Under Review
5. Track reviewer name and timestamp

---

## Security Notes

⚠️ **Important:**
- These are development/demo credentials
- Change passwords in production environment
- The system stores reviewer information with each decision
- All actions are timestamped and auditable

---

## Database Update

The credentials have been added to the PostgreSQL database using the `seed_users.py` script.

To manually add or update users:
```bash
cd backend
python seed_users.py
```

---

## Support

For technical issues or questions:
- Check `GOVERNMENT-PORTAL-GUIDE.md` for detailed usage instructions
- Review `ML-INTEGRATION-GUIDE.md` for ML system details
- See `SETUP-GUIDE.md` for installation help
