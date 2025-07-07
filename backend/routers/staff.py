"""
Staff management router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import Staff, Department, Subject
from backend.schemas.schemas import StaffCreate, StaffUpdate, StaffResponse
from backend.utils.security import get_current_user, hash_password

router = APIRouter()

@router.get("/", response_model=List[StaffResponse])
async def get_staff(
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all staff members"""
    query = db.query(Staff)
    
    # Filter by department if specified
    if department_id:
        query = query.filter(Staff.department_id == department_id)
    
    # If user is department admin, only show their department staff
    if current_user["user_type"] == "staff" and current_user["user"].is_department_admin:
        query = query.filter(Staff.department_id == current_user["user"].department_id)
    
    staff_members = query.all()
    return staff_members

@router.post("/", response_model=StaffResponse)
async def create_staff(
    staff: StaffCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new staff member"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Check if email already exists
    existing = db.query(Staff).filter(Staff.email == staff.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Validate department
    department = db.query(Department).filter(Department.id == staff.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid department"
        )
    
    # Set max subjects based on role
    max_subjects = 2 if staff.role == "Assistant Professor" else 1
    
    db_staff = Staff(
        name=staff.name,
        email=staff.email,
        password_hash=hash_password(staff.password),
        role=staff.role,
        department_id=staff.department_id,
        is_department_admin=staff.is_department_admin,
        max_subjects=max_subjects
    )
    
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    
    return db_staff

@router.get("/{staff_id}", response_model=StaffResponse)
async def get_staff_member(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get staff member by ID"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    return staff

@router.put("/{staff_id}", response_model=StaffResponse)
async def update_staff(
    staff_id: int,
    staff_update: StaffUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            if current_user["user"].id != staff_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
    
    # Update fields
    update_data = staff_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(staff, field, value)
    
    db.commit()
    db.refresh(staff)
    
    return staff

@router.delete("/{staff_id}")
async def delete_staff(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete staff member"""
    if current_user["user_type"] != "main_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only main admin can delete staff"
        )
    
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    # Check if staff has assigned subjects
    subject_count = db.query(Subject).filter(Subject.assigned_staff_id == staff_id).count()
    if subject_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete staff with assigned subjects"
        )
    
    db.delete(staff)
    db.commit()
    
    return {"message": "Staff member deleted successfully"}

@router.get("/{staff_id}/subjects")
async def get_staff_subjects(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get subjects assigned to staff member"""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff member not found"
        )
    
    subjects = db.query(Subject).filter(Subject.assigned_staff_id == staff_id).all()
    return subjects