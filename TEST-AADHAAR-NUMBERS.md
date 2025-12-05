# Test Aadhaar Numbers for Farmer Portal

## Aadhaar Numbers WITH Land (Can Submit Applications)

Use these Aadhaar numbers to test the application form. These people have registered land and can apply for subsidies.

### Format: `Aadhaar Number | Name | Land (acres) | Location`

1. **130767339629** | Lalita Rani | 13.89 acres | Belgaum, Karnataka
2. **645259966200** | Harish Singh | 15.08 acres | Guntur, Andhra Pradesh
3. **412482182246** | Padma Devi | 1.73 acres | Coimbatore, Tamil Nadu
4. **388344730956** | Rakesh Verma | 9.87 acres | Coimbatore, Tamil Nadu
5. **237277529229** | Naveen Patel | 12.36 acres | Coimbatore, Tamil Nadu
6. **111582479846** | Naveen Patel | 9.2 acres | Mysore, Karnataka
7. **891300410012** | Durga Rani | 13.24 acres | Bangalore Rural, Karnataka
8. **509662962715** | Ganesh Singh | 4.14 acres | Bangalore Rural, Karnataka
9. **779416023606** | Ramesh Naidu | 1.87 acres | Visakhapatnam, Andhra Pradesh
10. **758770853861** | Srikanth Naidu | 9.84 acres | Hyderabad, Telangana

## Aadhaar Numbers WITHOUT Land (Cannot Apply - Will Show Error)

These Aadhaar holders have NO registered land and cannot apply for subsidies.

1. **601400350509** | Ganesh Singh | 0 acres | Guntur, Andhra Pradesh
2. **656134121796** | Suresh Reddy | 0 acres | Mysore, Karnataka
3. **499430524665** | Durga Rani | 0 acres | Karimnagar, Telangana
4. **634068613279** | Harish Singh | 0 acres | Warangal, Telangana

## Testing Steps

### 1. Start the Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8002
```

### 2. Open Application Form
Open `frontend/application-form.html` in your browser

### 3. Test Workflow

**Scenario A: User WITH Land (Should Work)**
1. Enter Aadhaar: `130767339629` (formatted as `1307-6733-9629`)
2. Click "Verify Aadhaar"
3. ✅ System should:
   - Show green success message
   - Auto-fill: Name, Mobile, Land (13.89 acres), State, District, Address
   - Show "Eligible to apply" message
   - Display crop details section
4. Enter Crop Type: `Wheat` or `Paddy` or `Cotton`
5. Wait 1 second - subsidy calculations should appear automatically
6. ✅ Should show:
   - Fertilizer Subsidy: XX kg
   - Seed Subsidy: XX kg
7. Click "Submit Application"
8. ✅ Should show success with Application ID

**Scenario B: User WITHOUT Land (Should Fail)**
1. Enter Aadhaar: `601400350509`
2. Click "Verify Aadhaar"
3. ❌ System should show:
   - Red error message
   - "This Aadhaar holder has no registered land. Only farmers with land ownership can apply for subsidies."
4. Form should NOT proceed

## Common Crops to Test

- Paddy
- Wheat
- Cotton
- Sugarcane
- Maize
- Soybean

## Expected Behavior

1. **Aadhaar Verification**: Must verify before form appears
2. **Land Check**: Only land > 0 can proceed
3. **Auto-Fill**: All personal details filled from database
4. **Auto-Calculate**: Subsidies calculated based on crop + land
5. **Submit**: Only enabled after verification + calculation

## Troubleshooting

**If subsidies don't calculate:**
- Check if crop type is entered correctly
- Wait 1-2 seconds after typing
- Check browser console for errors
- Verify server is running on port 8002

**If Aadhaar verification fails:**
- Check if server is running
- Verify database has records (run `python -c "..."` from TEST-AADHAAR-NUMBERS.md)
- Check browser console for API errors
