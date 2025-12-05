# ðŸŽ¯ Farmer Portal - Complete Setup Guide

## ðŸ“‚ Project Location
Your project is located at:
```
C:\Users\arunk\OneDrive\Desktop\farmer-portal
```

## ðŸ“ Project Structure

```
farmer-portal/
â”‚
â”œâ”€â”€ ðŸ“„ README.md          â† Complete project documentation
â”œâ”€â”€ ðŸ“„ QUICKSTART.md      â† Quick start guide
â”‚
â”œâ”€â”€ ðŸ“ frontend/          â† All UI files
â”‚   â”œâ”€â”€ index.html               (Home page)
â”‚   â”œâ”€â”€ application-form.html    (Application form)
â”‚   â”œâ”€â”€ application-tracker.html (Track applications)
â”‚   â”œâ”€â”€ agriculture-login.html   (Agriculture dept login)
â”‚   â”œâ”€â”€ styles.css               (All styles)
â”‚   â”œâ”€â”€ app.js                   (Form logic)
â”‚   â”œâ”€â”€ tracker.js               (Tracker logic)
â”‚   â””â”€â”€ login.js                 (Login logic)
â”‚
â””â”€â”€ ðŸ“ backend/           â† FastAPI server
    â”œâ”€â”€ main.py                  (API server)
    â”œâ”€â”€ requirements.txt         (Python packages)
    â””â”€â”€ README.md                (Backend docs)
```

## ðŸŽ¬ Step-by-Step Setup

### Step 1: Install Backend Dependencies

Open PowerShell and run:

```powershell
cd C:\Users\arunk\OneDrive\Desktop\farmer-portal\backend
pip install -r requirements.txt
```

Expected output:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 pydantic-2.5.0 ...
```

### Step 2: Start the Backend Server

In the same PowerShell window:

```powershell
python main.py
```

Expected output:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

âœ… Backend is now running at `http://localhost:8000`

### Step 3: Open the Frontend

Open a NEW PowerShell window:

```powershell
cd C:\Users\arunk\OneDrive\Desktop\farmer-portal\frontend
Start-Process index.html
```

Your default browser will open with the Farmer Portal home page.

## ðŸ§ª Test Each Feature

### Test 1: Submit Application

1. Click **"Application Form"** in the navbar
2. Fill in test data:
   - Farmer Name: `Ramesh Kumar`
   - Aadhaar: `1234-5678-9012`
   - Mobile: `9876543210`
   - Address: `Village Kamlapuram, Dist. Rajnagar`
   - Land: `5.5` acres
   - Crop: `Rice`
   - Fertilizer: `NPK, Urea`
   - Department: `Agriculture`
3. Click **Submit Application**
4. âœ… You should see: "Application submitted successfully! Your Application ID is: APP20251205..."

### Test 2: Track Application

1. Click **"Application Tracker"** in the navbar
2. Enter the Application ID from Step 1
3. Enter mobile number: `9876543210`
4. Click **Track Application**
5. âœ… You should see application details with status "Pending"

### Test 3: Department Login

1. Click **"Agriculture Login"** in the navbar
2. Enter:
   - User ID: `admin`
   - Password: `admin123`
3. Click **Login**
4. âœ… You should see: "Login successful! Welcome, Agriculture Admin"

## ðŸŒ Available URLs

Once running, you can access:

- **Home Page**: Open `index.html` in browser
- **API Documentation**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **API Base**: http://localhost:8000

## ðŸ”‘ Login Credentials Reference

| Department      | User ID   | Password   | Role    |
|-----------------|-----------|------------|---------|
| Agriculture     | admin     | admin123   | Admin   |
| Agriculture     | officer1  | officer123 | Officer |

## ðŸŽ¨ UI Features Included

âœ… **Navigation Bar** with all menu items
âœ… **Home Page** with hero section and quick actions
âœ… **Application Form** with validation
âœ… **Application Tracker** with status display
âœ… **Agriculture Login** page
âœ… **Government portal theme** (blue & white)
âœ… **Responsive design** for mobile/desktop
âœ… **Form validation** and error handling
âœ… **Status badges** (Approved/Pending/Rejected)
âœ… **Font Awesome icons** throughout

## ðŸ”§ Troubleshooting

### Backend won't start?
```powershell
# Check if Python is installed
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend shows "Network error"?
- Make sure backend server is running on port 8000
- Check: http://localhost:8000/health

### Port 8000 already in use?
```powershell
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

## ðŸ“š Next Steps

1. âœ… Test all features
2. ðŸ“– Read `README.md` for detailed documentation
3. ðŸ”§ Customize as needed
4. ðŸš€ Deploy to production (with proper database and security)

## ðŸ’¡ Tips

- Keep the backend PowerShell window open while testing
- Use Ctrl+C in the backend window to stop the server
- Refresh the browser page to see updates
- Check browser console (F12) for any JavaScript errors
- Check the API docs at http://localhost:8000/docs for testing endpoints

---

**ðŸŽ‰ Your Farmer Portal is ready to use!**

For detailed information, see `README.md`
For quick commands, see `QUICKSTART.md`

