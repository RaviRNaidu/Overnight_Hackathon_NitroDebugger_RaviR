from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import random
import string
import pandas as pd
from fraud_detector import SubsidyFraudDetector
from sqlalchemy.orm import Session
from database import get_db, init_db, Application, User

app = FastAPI(title="Farmer Portal API", version="1.0.0")

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")

# Initialize fraud detector
fraud_detector = SubsidyFraudDetector(crop_norms_path='data/crop_norms.csv')

# CORS configuration to allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ApplicationCreate(BaseModel):
    farmer_name: str = Field(..., min_length=2, max_length=100)
    aadhaar_number: str = Field(..., pattern=r"^\d{4}-\d{4}-\d{4}$")
    mobile_number: str = Field(..., pattern=r"^\d{10}$")
    state: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=10, max_length=500)
    total_land_acres: float = Field(..., gt=0)
    crop_type: str = Field(..., min_length=2, max_length=100)
    fertilizer_qty: float = Field(..., ge=0, description="Requested fertilizer quantity in kg")
    seed_qty: float = Field(..., ge=0, description="Requested seed quantity in kg")

class EligibilityCheckRequest(BaseModel):
    crop_type: str = Field(..., min_length=1)
    land_size_acres: float = Field(..., gt=0)
    requested_qty: float = Field(..., ge=0)
    subsidy_type: str = Field(default='fertilizer')

class ApplicationResponse(BaseModel):
    application_id: str
    farmer_name: str
    aadhaar_number: str
    mobile_number: str
    state: str
    district: str
    address: str
    total_land_acres: float
    crop_type: str
    fertilizer_qty: float
    seed_qty: float
    status: str
    submitted_date: datetime

class LoginRequest(BaseModel):
    user_id: str
    password: str
    department: str = "agriculture"  # Default to agriculture

class LoginResponse(BaseModel):
    success: bool
    user_name: str
    department: str
    token: Optional[str] = None

# Utility Functions
def generate_application_id():
    """Generate unique application ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"APP{timestamp}{random_suffix}"

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Farmer Portal API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/applications", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """Create a new farmer application"""
    try:
        app_id = generate_application_id()
        
        # Create database application object
        db_application = Application(
            application_id=app_id,
            farmer_name=application.farmer_name,
            aadhaar_number=application.aadhaar_number,
            mobile_number=application.mobile_number,
            state=application.state,
            district=application.district,
            address=application.address,
            total_land_acres=application.total_land_acres,
            crop_type=application.crop_type,
            fertilizer_qty=application.fertilizer_qty,
            seed_qty=application.seed_qty,
            status="Pending"
        )
        
        db.add(db_application)
        db.commit()
        db.refresh(db_application)
        
        return {
            "success": True,
            "message": "Application submitted successfully",
            "application_id": app_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )

@app.get("/api/applications/{application_id}", response_model=ApplicationResponse)
async def get_application(application_id: str, mobile_number: str):
    """Get application details by ID and mobile number"""
    
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application = applications_db[application_id]
    
    # Verify mobile number matches
    if application["mobile_number"] != mobile_number:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mobile number does not match application records"
        )
    
    return application

@app.get("/api/applications", response_model=list[ApplicationResponse])
async def get_all_applications(department: Optional[str] = None):
    """Get all applications, optionally filtered by department"""
    
    if department:
        filtered_apps = [
            app for app in applications_db.values() 
            if app["department"] == department
        ]
        return filtered_apps
    
    return list(applications_db.values())

@app.post("/api/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """Authenticate department users"""
    
    department = credentials.department
    user_id = credentials.user_id
    password = credentials.password
    
    # Check if department exists
    if department not in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid department"
        )
    
    # Check if user exists
    if user_id not in users_db[department]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID or password"
        )
    
    # Verify password
    user = users_db[department][user_id]
    if user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID or password"
        )
    
    # Generate token (simplified - use JWT in production)
    token = f"token_{department}_{user_id}_{datetime.now().timestamp()}"
    
    return {
        "success": True,
        "user_name": user["name"],
        "department": department,
        "token": token
    }

@app.put("/api/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status: Literal["Approved", "Pending", "Rejected"]
):
    """Update application status (for department use)"""
    
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    applications_db[application_id]["status"] = status
    
    return {
        "success": True,
        "message": f"Application status updated to {status}",
        "application_id": application_id
    }

@app.delete("/api/applications/{application_id}")
async def delete_application(application_id: str):
    """Delete an application (admin use)"""
    
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    del applications_db[application_id]
    
    return {
        "success": True,
        "message": "Application deleted successfully"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "total_applications": len(applications_db)
    }

# Fraud Detection Endpoints
@app.get("/api/fraud-analysis")
async def get_fraud_analysis():
    """
    Analyze all applications for fraud patterns.
    Returns statistics and flagged applications.
    """
    try:
        if not applications_db:
            return {
                "message": "No applications to analyze",
                "statistics": {
                    "total_applications": 0,
                    "flagged_anomalies": 0,
                    "anomaly_percentage": 0,
                    "high_risk_count": 0,
                    "medium_risk_count": 0,
                    "low_risk_count": 0
                },
                "flagged_applications": []
            }
        
        # Convert applications to DataFrame
        apps_list = list(applications_db.values())
        apps_df = pd.DataFrame(apps_list)
        
        # Perform fraud detection
        stats = fraud_detector.get_fraud_statistics(apps_df)
        
        return {
            "message": "Fraud analysis completed successfully",
            "statistics": {
                "total_applications": stats['total_applications'],
                "flagged_anomalies": stats['flagged_anomalies'],
                "anomaly_percentage": round(stats['anomaly_percentage'], 2),
                "high_risk_count": stats['high_risk_count'],
                "medium_risk_count": stats['medium_risk_count'],
                "low_risk_count": stats['low_risk_count']
            },
            "flagged_applications": stats['top_risk_applications']
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud analysis failed: {str(e)}"
        )

@app.get("/api/fraud-analysis/{application_id}")
async def get_application_fraud_score(application_id: str):
    """
    Get fraud risk score for a specific application.
    """
    try:
        if not applications_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No applications found"
            )
        
        if application_id not in applications_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Convert applications to DataFrame
        apps_list = list(applications_db.values())
        apps_df = pd.DataFrame(apps_list)
        
        # Get fraud predictions
        results = fraud_detector.predict_anomalies(apps_df)
        
        # Find specific application result
        app_result = results[results['application_id'] == application_id]
        
        if app_result.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fraud score not available for this application"
            )
        
        result = app_result.iloc[0]
        
        return {
            "application_id": application_id,
            "risk_level": result['risk_level'],
            "anomaly_score": round(float(result['anomaly_score']), 3),
            "is_anomaly": bool(result['is_anomaly']),
            "fraud_indicators": result['fraud_indicators'],
            "details": {
                "land_acres": float(result['land_acres']),
                "district_density": int(result['district_density']),
                "land_deviation": round(float(result['land_deviation']), 2)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating fraud score: {str(e)}"
        )

@app.post("/api/check-eligibility")
async def check_eligibility(request: EligibilityCheckRequest):
    """
    Check if requested subsidy quantity is within allowed limits.
    Real-time fraud prevention (USE CASE 2).
    
    Args:
        request: EligibilityCheckRequest with crop_type, land_size_acres, requested_qty, subsidy_type
    
    Returns:
        Eligibility status with allowed quantity and fraud indicators
    """
    try:
        # Validate inputs
        if request.land_size_acres <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land size must be greater than 0"
            )
        
        if request.requested_qty < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity cannot be negative"
            )
        
        if request.subsidy_type not in ['fertilizer', 'seed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="subsidy_type must be 'fertilizer' or 'seed'"
            )
        
        # Check eligibility using fraud detector
        result = fraud_detector.check_eligibility(
            crop_type=request.crop_type,
            land_size_acres=request.land_size_acres,
            requested_qty=request.requested_qty,
            subsidy_type=request.subsidy_type
        )
        
        return {
            "approved": result['approved'],
            "reason": result['reason'],
            "risk_flag": result['risk_flag'],
            "allowed_qty": result['allowed_qty'],
            "requested_qty": result['requested_qty'],
            "qty_ratio": result['qty_ratio'],
            "rate_per_acre": result['rate_per_acre'],
            "fraud_indicators": result['fraud_indicators'],
            "crop_type": request.crop_type,
            "land_size_acres": request.land_size_acres,
            "subsidy_type": request.subsidy_type
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Eligibility check failed: {str(e)}"
        )
@app.post("/api/train-fraud-model")
async def train_fraud_model(contamination: float = 0.1):
    """
    Train/retrain the fraud detection model on current applications.
    Contamination is the expected proportion of outliers (default 10%).
    """
    try:
        if not applications_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No applications available for training"
            )
        
        # Convert applications to DataFrame
        apps_list = list(applications_db.values())
        apps_df = pd.DataFrame(apps_list)
        
        # Train model
        fraud_detector.train(apps_df, contamination=contamination)
        
        return {
            "success": True,
            "message": f"Fraud detection model trained on {len(apps_df)} applications",
            "contamination_rate": contamination
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


