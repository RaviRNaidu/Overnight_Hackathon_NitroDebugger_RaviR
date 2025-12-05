# Government Portal - Accept/Reject Testing Guide

## Overview
The government portal now has **Quick Accept/Reject** buttons with complete backend integration and SMS notifications.

## Features Implemented

### ✅ Frontend Features
1. **Quick Action Buttons** in the applications table:
   - ✓ Green checkmark button for **Approve**
   - ✗ Red X button for **Reject**
   - Buttons only appear for applications with status: `pending` or `under_review`

2. **Enhanced UI**:
   - Buttons display farmer details in prompts
   - Pre-filled default comments for faster processing
   - Confirmation dialog for rejections
   - Success messages show SMS notification status

### ✅ Backend Features
1. **Status Update Endpoint**: `PUT /api/applications/{application_id}/status`
   - Accepts: `status`, `review_comments`, `reviewed_by`
   - Updates application status in database
   - Records reviewer name and timestamp
   - Returns success status with notification info

2. **SMS Notifications**:
   - **Approved**: Sends subsidy details (fertilizer + seed quantities)
   - **Rejected**: Sends rejection reason
   - SMS messages printed to server console for verification

## Testing Steps

### 1. Start the Server (Already Running)
```bash
Backend server running on: http://localhost:8002
```

### 2. Create Test Applications
1. Open: `frontend/application-form.html`
2. Use test Aadhaar: `1307-6733-9629` (has 13.89 acres)
3. Enter crop: `Wheat` or `Paddy`
4. Submit application
5. Note the Application ID

### 3. Access Government Portal
1. Open: `frontend/government-login.html`
2. Login credentials:
   - **User ID**: `officer1` or `admin`
   - **Password**: `password123`
3. You'll be redirected to `government-portal.html`

### 4. Test Quick Approve
1. Find a **Pending** application in the table
2. Click the **✓** (green checkmark) button
3. You should see a prompt showing:
   ```
   ✓ APPROVE Application APP-XXXX
   
   Farmer: [Name]
   Crop: [Crop Type]
   Land: [Acres] acres
   
   Enter approval comments (required):
   ```
4. Default text: `Application meets all eligibility criteria. Approved for subsidy.`
5. Click OK
6. Success message shows:
   ```
   ✓ Application APP-XXXX APPROVED successfully!
   
   📱 SMS notification sent to farmer (XXXXXXXXXX):
   "Your application APP-XXXX has been APPROVED. Fertilizer: XXkg, Seeds: XXkg..."
   ```
7. Check **backend terminal** for SMS notification:
   ```
   ================================================================================
   SMS NOTIFICATION to XXXXXXXXXX
   Message: Your application APP-XXXX has been APPROVED. Fertilizer: XXkg, Seeds: XXkg. Collect from nearest center. -Dept of Agriculture
   ================================================================================
   ```

### 5. Test Quick Reject
1. Find another **Pending** application
2. Click the **✗** (red X) button
3. You should see a prompt:
   ```
   ✗ REJECT Application APP-XXXX
   
   Farmer: [Name]
   Crop: [Crop Type]
   Land: [Acres] acres
   
   Enter rejection reason (required):
   ```
4. Default text: `Insufficient land ownership verification.`
5. Enter reason and click OK
6. Confirmation dialog appears:
   ```
   Are you sure you want to REJECT application APP-XXXX?
   
   This will notify the farmer via SMS.
   ```
7. Click OK
8. Success message shows SMS notification
9. Check **backend terminal** for rejection SMS

### 6. Verify Database Updates
Applications should now show:
- **Status**: Changed to `approved` or `rejected`
- **Review Comments**: The comments you entered
- **Reviewed By**: Officer name from login session
- **Reviewed At**: Timestamp of the action
- Buttons disappear (only show for pending/under_review)

## Expected Behavior

### Approval Flow
1. Officer clicks ✓ → Prompt with farmer details
2. Enter comments → Click OK
3. Backend updates status to "approved"
4. SMS notification generated
5. Database records reviewer info
6. Table refreshes automatically
7. Success alert shows SMS sent

### Rejection Flow
1. Officer clicks ✗ → Prompt with farmer details
2. Enter rejection reason → Click OK
3. Confirmation dialog → Click OK
4. Backend updates status to "rejected"
5. SMS notification with reason sent
6. Database records reviewer info
7. Table refreshes automatically
8. Alert shows SMS sent

## SMS Notification Examples

### Approved Application
```
Your application APP-123456 has been APPROVED. 
Fertilizer: 25.5kg, Seeds: 12.75kg. 
Collect from nearest center. 
-Dept of Agriculture
```

### Rejected Application
```
Your application APP-123456 has been REJECTED. 
Reason: Insufficient land ownership verification. 
For queries, contact Dept of Agriculture. 
-Govt Portal
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Application status updated to approved",
  "application_id": "APP-123456",
  "new_status": "approved",
  "sms_sent": true,
  "notification": "Your application APP-123456 has been APPROVED..."
}
```

### Error Response
```json
{
  "detail": "Application not found"
}
```

## Troubleshooting

### Buttons Not Showing
- Check application status (must be `pending` or `under_review`)
- Refresh the page to reload applications
- Verify JavaScript console for errors

### Status Not Updating
- Check backend server is running on port 8002
- Check browser console for API errors
- Verify CORS is enabled (already configured)

### SMS Not Showing in Console
- Check backend terminal output
- Ensure status is `approved` or `rejected`
- Verify the print statements in `main.py`

## Technical Details

### Frontend Files Modified
- `frontend/government-portal.html`:
  - Added ✓/✗ buttons in table (lines ~720)
  - Enhanced `quickApprove()` function with better prompts
  - Enhanced `quickReject()` function with confirmation
  - Improved success messages with SMS notification display

### Backend Files Modified
- `backend/main.py`:
  - Enhanced `/api/applications/{id}/status` endpoint
  - Added SMS notification generation
  - Added `sms_sent` and `notification` to response
  - Console logging for SMS messages

### Database Schema
Applications table includes:
- `status`: "pending" | "under_review" | "approved" | "rejected"
- `review_comments`: Text field for officer comments
- `reviewed_by`: Officer name
- `reviewed_at`: Timestamp

## Quick Reference

### Test Credentials
- **Officer Login**: `officer1` / `password123`
- **Admin Login**: `admin` / `password123`

### Test Aadhaar Numbers (with land)
- `1307-6733-9629` (13.89 acres)
- `6452-5996-6200` (15.08 acres)
- `4124-8218-2246` (1.73 acres)

### Common Test Crops
- Paddy, Wheat, Cotton, Sugarcane, Maize, Soybean

## Next Steps
1. Test both approve and reject flows
2. Verify SMS messages in backend console
3. Check database updates persist
4. Test with multiple applications
5. Verify table updates automatically after actions

---
**Status**: ✅ All features implemented and ready for testing
**Server**: Running on http://localhost:8002
**Last Updated**: December 5, 2025
