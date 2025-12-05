# Farmer Portal Backend

FastAPI-based backend for the Farmer Portal application.

## Features

- RESTful API for farmer applications
- Department login authentication (Agriculture)
- Application tracking and status management
- CORS enabled for frontend integration

## API Endpoints

### Applications
- `POST /api/applications` - Create new application
- `GET /api/applications/{id}` - Get application by ID
- `GET /api/applications` - Get all applications
- `PUT /api/applications/{id}/status` - Update application status
- `DELETE /api/applications/{id}` - Delete application

### Authentication
- `POST /api/login` - Department user login

### Health Check
- `GET /health` - API health status

## Default Credentials

### Agriculture Department
- User ID: `admin` | Password: `admin123`
- User ID: `officer1` | Password: `officer123`


## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python main.py
   ```

3. API will be available at: `http://localhost:8000`

4. API documentation: `http://localhost:8000/docs`

## Note
This implementation uses in-memory storage. For production, integrate with a proper database like PostgreSQL or MongoDB.

