"""
Timetable management router with AI-powered generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database.database import get_db
from backend.database.models import TimetableEntry, Subject, Staff, Classroom, TimeSlot, Department
from backend.schemas.schemas import (
    TimetableEntryCreate, TimetableEntryResponse, 
    TimetableGenerateRequest, TimetableResponse
)
from backend.utils.security import get_current_user
from backend.utils.ai_service import ai_service
import pandas as pd
from io import BytesIO

router = APIRouter()

@router.get("/", response_model=List[TimetableEntryResponse])
async def get_timetable(
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    staff_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get timetable entries"""
    query = db.query(TimetableEntry)
    
    # Apply filters
    if department_id:
        query = query.filter(TimetableEntry.department_id == department_id)
    if semester:
        query = query.filter(TimetableEntry.semester == semester)
    if section:
        query = query.filter(TimetableEntry.section == section)
    if staff_id:
        query = query.filter(TimetableEntry.staff_id == staff_id)
    
    # If user is staff, filter by their department
    if current_user["user_type"] == "staff":
        query = query.filter(TimetableEntry.department_id == current_user["user"].department_id)
    
    entries = query.all()
    return entries

@router.post("/generate", response_model=TimetableResponse)
async def generate_timetable(
    request: TimetableGenerateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI-powered timetable"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Validate department
    department = db.query(Department).filter(Department.id == request.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Get required data
    subjects = db.query(Subject).filter(
        Subject.department_id == request.department_id,
        Subject.semester == request.semester,
        Subject.assigned_staff_id.isnot(None)
    ).all()
    
    if not subjects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No assigned subjects found for this department and semester"
        )
    
    staff = db.query(Staff).filter(Staff.department_id == request.department_id).all()
    classrooms = db.query(Classroom).filter(
        Classroom.department_id == request.department_id,
        Classroom.is_available == True
    ).all()
    time_slots = db.query(TimeSlot).filter(TimeSlot.is_active == True).all()
    
    # Prepare data for AI
    subjects_data = [
        {
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "assigned_staff_id": s.assigned_staff_id,
            "theory_hours": s.theory_hours,
            "practical_hours": s.practical_hours,
            "credits": s.credits
        }
        for s in subjects
    ]
    
    staff_data = [
        {
            "id": s.id,
            "name": s.name,
            "role": s.role,
            "max_subjects": s.max_subjects
        }
        for s in staff
    ]
    
    classrooms_data = [
        {
            "id": c.id,
            "room_number": c.room_number,
            "capacity": c.capacity,
            "room_type": c.room_type
        }
        for c in classrooms
    ]
    
    time_slots_data = [
        {
            "id": t.id,
            "slot_name": t.slot_name,
            "start_time": str(t.start_time),
            "end_time": str(t.end_time)
        }
        for t in time_slots
    ]
    
    constraints = {
        "department_id": request.department_id,
        "semester": request.semester,
        "section": request.section,
        "max_hours_per_day": 6,
        "lunch_break": {"start": "13:15", "end": "14:00"}
    }
    
    # Clear existing timetable for this department, semester, and section
    db.query(TimetableEntry).filter(
        TimetableEntry.department_id == request.department_id,
        TimetableEntry.semester == request.semester,
        TimetableEntry.section == request.section
    ).delete()
    
    # Generate timetable using AI
    ai_result = ai_service.generate_timetable_suggestions(
        subjects_data, staff_data, classrooms_data, time_slots_data, constraints
    )
    
    # Create timetable entries
    created_entries = []
    for entry_data in ai_result.get("timetable", []):
        entry = TimetableEntry(
            day=entry_data["day"],
            time_slot_id=entry_data["time_slot_id"],
            subject_id=entry_data["subject_id"],
            staff_id=entry_data["staff_id"],
            classroom_id=entry_data["classroom_id"],
            department_id=request.department_id,
            semester=request.semester,
            section=request.section
        )
        db.add(entry)
        created_entries.append(entry)
    
    db.commit()
    
    # Refresh entries to get IDs
    for entry in created_entries:
        db.refresh(entry)
    
    return TimetableResponse(
        entries=created_entries,
        total_entries=len(created_entries),
        conflicts=ai_result.get("conflicts", [])
    )

@router.get("/export")
async def export_timetable(
    department_id: int,
    semester: int,
    section: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export timetable to Excel"""
    # Get timetable entries
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.department_id == department_id,
        TimetableEntry.semester == semester,
        TimetableEntry.section == section
    ).all()
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No timetable found for the specified criteria"
        )
    
    # Get related data
    time_slots = {ts.id: ts for ts in db.query(TimeSlot).all()}
    subjects = {s.id: s for s in db.query(Subject).all()}
    staff = {st.id: st for st in db.query(Staff).all()}
    classrooms = {c.id: c for c in db.query(Classroom).all()}
    
    # Prepare data for Excel
    timetable_data = []
    for entry in entries:
        time_slot = time_slots.get(entry.time_slot_id)
        subject = subjects.get(entry.subject_id)
        staff_member = staff.get(entry.staff_id)
        classroom = classrooms.get(entry.classroom_id)
        
        timetable_data.append({
            "Day": entry.day,
            "Time Slot": time_slot.slot_name if time_slot else "",
            "Start Time": str(time_slot.start_time) if time_slot else "",
            "End Time": str(time_slot.end_time) if time_slot else "",
            "Subject": subject.name if subject else "",
            "Subject Code": subject.code if subject else "",
            "Staff": staff_member.name if staff_member else "",
            "Classroom": classroom.room_number if classroom else "",
            "Room Type": classroom.room_type if classroom else "",
            "Semester": entry.semester,
            "Section": entry.section
        })
    
    # Create DataFrame
    df = pd.DataFrame(timetable_data)
    
    # Create Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Timetable', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Timetable']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    
    # Get department name for filename
    department = db.query(Department).filter(Department.id == department_id).first()
    dept_name = department.code if department else "DEPT"
    filename = f"Timetable_{dept_name}_Sem{semester}_Sec{section}.xlsx"
    
    return Response(
        content=output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/clear")
async def clear_timetable(
    department_id: int,
    semester: int,
    section: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Clear timetable for specific department, semester, and section"""
    # Check permissions
    if current_user["user_type"] != "main_admin":
        if not (current_user["user_type"] == "staff" and current_user["user"].is_department_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
    
    # Delete entries
    deleted_count = db.query(TimetableEntry).filter(
        TimetableEntry.department_id == department_id,
        TimetableEntry.semester == semester,
        TimetableEntry.section == section
    ).delete()
    
    db.commit()
    
    return {"message": f"Cleared {deleted_count} timetable entries"}

@router.get("/conflicts")
async def check_conflicts(
    department_id: int,
    semester: int,
    section: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Check for conflicts in timetable"""
    entries = db.query(TimetableEntry).filter(
        TimetableEntry.department_id == department_id,
        TimetableEntry.semester == semester,
        TimetableEntry.section == section
    ).all()
    
    if not entries:
        return {"conflicts": [], "message": "No timetable found"}
    
    # Convert to format expected by AI service
    entries_data = [
        {
            "day": e.day,
            "time_slot_id": e.time_slot_id,
            "staff_id": e.staff_id,
            "classroom_id": e.classroom_id
        }
        for e in entries
    ]
    
    conflicts = ai_service.detect_conflicts(entries_data)
    suggestions = ai_service.optimize_timetable(entries_data)
    
    return {
        "conflicts": conflicts,
        "suggestions": suggestions,
        "total_entries": len(entries)
    }