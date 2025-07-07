"""
Subject management router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import Subject, Department, Staff
from backend.schemas.schemas import SubjectCreate, SubjectUpdate, SubjectResponse
from backend.utils.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[SubjectResponse])
async def get_subjects(
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all subjects"""
    query = db.query(Subject)
    
    # Filter by department if specified
    if department_id:
        query = query.filter(Subject.department_id == department_id)
    
    # Filter by semester if specified
    if semester:
        query = query.filter(Subject.semester == semester)
    
    # If user is department admin, only show their department subjects
    if current_user["user_type"] == "staff" and current_user["user"].is_department_admin:
        query = query.filter(Subject.department_id == current_user["user"].department_id)
    
    subjects = query.all()
    return subjects

@router.post("/", response_model=SubjectResponse)
async def create_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new subject"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Check if subject code already exists
    existing = db.query(Subject).filter(Subject.code == subject.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject code already exists"
        )
    
    # Validate department
    department = db.query(Department).filter(Department.id == subject.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid department"
        )
    
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    
    return db_subject

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get subject by ID"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    return subject

@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_update: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update subject"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Update fields
    for field, value in subject_update.dict(exclude_unset=True).items():
        setattr(subject, field, value)
    
    db.commit()
    db.refresh(subject)
    
    return subject

@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete subject"""
    if current_user["user_type"] != "main_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only main admin can delete subjects"
        )
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    db.delete(subject)
    db.commit()
    
    return {"message": "Subject deleted successfully"}

@router.post("/{subject_id}/assign/{staff_id}")
async def assign_subject_to_staff(
    subject_id: int,
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Assign subject to staff member"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    # Check if subject is already assigned
    if subject.assigned_staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject is already assigned to another staff member"
        )
    
    # Check staff's subject limit
    current_subjects = db.query(Subject).filter(Subject.assigned_staff_id == staff_id).count()
    if current_subjects >= staff.max_subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Staff member has reached maximum subject limit ({staff.max_subjects})"
        )
    
    # Assign subject
    subject.assigned_staff_id = staff_id
    db.commit()
    db.refresh(subject)
    
    return {"message": "Subject assigned successfully", "subject": subject}

@router.delete("/{subject_id}/unassign")
async def unassign_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Unassign subject from staff member"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    if not subject.assigned_staff_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject is not assigned to any staff member"
        )
    
    # Unassign subject
    subject.assigned_staff_id = None
    db.commit()
    db.refresh(subject)
    
    return {"message": "Subject unassigned successfully", "subject": subject}