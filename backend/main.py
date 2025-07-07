"""
FastAPI Backend Server for SRM Timetable Management System
Provides RESTful APIs for all timetable management operations
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from backend.routers import auth, departments, staff, subjects, timetable, classrooms
from backend.database.database import engine, Base

# Create FastAPI app
app = FastAPI(
    title="SRM Timetable Management API",
    description="Complete API for SRM College Ramapuram Timetable Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(departments.router, prefix="/api/departments", tags=["Departments"])
app.include_router(staff.router, prefix="/api/staff", tags=["Staff"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["Subjects"])
app.include_router(timetable.router, prefix="/api/timetable", tags=["Timetable"])
app.include_router(classrooms.router, prefix="/api/classrooms", tags=["Classrooms"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SRM Timetable Management API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SRM Timetable API"}

def start_fastapi_server():
    """Start FastAPI server"""
    uvicorn.run(
        "backend.main:app",
        host=os.getenv('FASTAPI_HOST', '127.0.0.1'),
        port=int(os.getenv('FASTAPI_PORT', 8000)),
        reload=os.getenv('FLASK_ENV') == 'development',
        log_level="info"
    )

if __name__ == "__main__":
    start_fastapi_server()