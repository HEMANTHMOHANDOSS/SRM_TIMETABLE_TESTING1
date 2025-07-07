"""
Classroom management router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import Classroom, Department
from backend.schemas.schemas import ClassroomCreate, ClassroomUpdate, ClassroomResponse
from backend.utils.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ClassroomResponse])
async def get_classrooms(
    department_id: Optional[int] = None,
    room_type: Optional[str] = None,
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all classrooms"""
    query = db.query(Classroom)
    
    # Filter by department if specified
    if department_id:
        query = query.filter(Classroom.department_id == department_id)
    
    # Filter by room type if specified
    if room_type:
        query = query.filter(Classroom.room_type == room_type)
    
    # Filter by availability if specified
    if available_only:
        query = query.filter(Classroom.is_available == True)
    
    classrooms = query.all()
    return classrooms

@router.post("/", response_model=ClassroomResponse)
async def create_classroom(
    classroom: ClassroomCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new classroom"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Check if room number already exists
    existing = db.query(Classroom).filter(Classroom.room_number == classroom.room_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room number already exists"
        )
    
    # Validate department if specified
    if classroom.department_id:
        department = db.query(Department).filter(Department.id == classroom.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid department"
            )
    
    db_classroom = Classroom(**classroom.dict())
    db.add(db_classroom)
    db.commit()
    db.refresh(db_classroom)
    
    return db_classroom

@router.get("/{classroom_id}", response_model=ClassroomResponse)
async def get_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get classroom by ID"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    return classroom

@router.put("/{classroom_id}", response_model=ClassroomResponse)
async def update_classroom(
    classroom_id: int,
    classroom_update: ClassroomUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update classroom"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Update fields
    for field, value in classroom_update.dict(exclude_unset=True).items():
        setattr(classroom, field, value)
    
    db.commit()
    db.refresh(classroom)
    
    return classroom

@router.delete("/{classroom_id}")
async def delete_classroom(
    classroom_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete classroom"""
    if current_user["user_type"] != "main_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only main admin can delete classrooms"
        )
    
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Classroom not found"
        )
    
    db.delete(classroom)
    db.commit()
    
    return {"message": "Classroom deleted successfully"}