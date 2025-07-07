"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, time

# Authentication Schemas
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    user_type: str = "staff"  # staff or main_admin

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str
    department_id: int

# Department Schemas
class DepartmentBase(BaseModel):
    name: str
    code: str
    admin_id: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    admin_id: Optional[int] = None

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Staff Schemas
class StaffBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    department_id: int
    is_department_admin: bool = False
    max_subjects: int = 1

class StaffCreate(StaffBase):
    password: str

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[int] = None
    is_department_admin: Optional[bool] = None
    max_subjects: Optional[int] = None

class StaffResponse(StaffBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    code: str
    department_id: int
    credits: int = 3
    theory_hours: int = 3
    practical_hours: int = 0
    semester: int

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    department_id: Optional[int] = None
    assigned_staff_id: Optional[int] = None
    credits: Optional[int] = None
    theory_hours: Optional[int] = None
    practical_hours: Optional[int] = None
    semester: Optional[int] = None

class SubjectResponse(SubjectBase):
    id: int
    assigned_staff_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Classroom Schemas
class ClassroomBase(BaseModel):
    room_number: str
    capacity: int
    room_type: str = "Theory"
    department_id: Optional[int] = None
    is_available: bool = True

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomUpdate(BaseModel):
    room_number: Optional[str] = None
    capacity: Optional[int] = None
    room_type: Optional[str] = None
    department_id: Optional[int] = None
    is_available: Optional[bool] = None

class ClassroomResponse(ClassroomBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Timetable Schemas
class TimetableEntryBase(BaseModel):
    day: str
    time_slot_id: int
    subject_id: int
    staff_id: int
    classroom_id: int
    department_id: int
    semester: int
    section: str

class TimetableEntryCreate(TimetableEntryBase):
    pass

class TimetableEntryResponse(TimetableEntryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TimetableGenerateRequest(BaseModel):
    department_id: int
    semester: int
    section: str

class TimetableResponse(BaseModel):
    entries: List[TimetableEntryResponse]
    total_entries: int
    conflicts: List[str] = []

# Time Slot Schemas
class TimeSlotBase(BaseModel):
    slot_name: str
    start_time: time
    end_time: time
    is_active: bool = True

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotResponse(TimeSlotBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# System Rule Schemas
class SystemRuleBase(BaseModel):
    rule_name: str
    rule_value: str
    rule_type: str
    description: Optional[str] = None

class SystemRuleCreate(SystemRuleBase):
    pass

class SystemRuleUpdate(BaseModel):
    rule_value: Optional[str] = None
    description: Optional[str] = None

class SystemRuleResponse(SystemRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True