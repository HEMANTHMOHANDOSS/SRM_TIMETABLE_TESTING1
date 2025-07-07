"""
SQLAlchemy Models for SRM Timetable Management System
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.database import Base

class MainAdmin(Base):
    """Main Administrator model"""
    __tablename__ = "main_admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Department(Base):
    """Department model"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    admin_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    staff_members = relationship("Staff", back_populates="department", foreign_keys="Staff.department_id")
    subjects = relationship("Subject", back_populates="department")
    classrooms = relationship("Classroom", back_populates="department")
    admin = relationship("Staff", foreign_keys=[admin_id], post_update=True)

class Staff(Base):
    """Staff model"""
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # Assistant Professor, Professor, HOD
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    is_department_admin = Column(Boolean, default=False)
    max_subjects = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="staff_members", foreign_keys=[department_id])
    assigned_subjects = relationship("Subject", back_populates="assigned_staff")
    timetable_entries = relationship("TimetableEntry", back_populates="staff")

class Subject(Base):
    """Subject model"""
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    credits = Column(Integer, default=3)
    theory_hours = Column(Integer, default=3)
    practical_hours = Column(Integer, default=0)
    semester = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="subjects")
    assigned_staff = relationship("Staff", back_populates="assigned_subjects")
    timetable_entries = relationship("TimetableEntry", back_populates="subject")

class Classroom(Base):
    """Classroom model"""
    __tablename__ = "classrooms"
    
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(20), default="Theory")  # Theory, Lab, Seminar
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="classrooms")
    timetable_entries = relationship("TimetableEntry", back_populates="classroom")

class TimeSlot(Base):
    """Time slot model"""
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    slot_name = Column(String(20), unique=True, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    timetable_entries = relationship("TimetableEntry", back_populates="time_slot")

class TimetableEntry(Base):
    """Timetable entry model"""
    __tablename__ = "timetable_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    day = Column(String(10), nullable=False)  # Monday, Tuesday, etc.
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String(5), nullable=False)  # A, B, C, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    time_slot = relationship("TimeSlot", back_populates="timetable_entries")
    subject = relationship("Subject", back_populates="timetable_entries")
    staff = relationship("Staff", back_populates="timetable_entries")
    classroom = relationship("Classroom", back_populates="timetable_entries")

class SystemRule(Base):
    """System rules model for dynamic configuration"""
    __tablename__ = "system_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), unique=True, nullable=False)
    rule_value = Column(String(255), nullable=False)
    rule_type = Column(String(20), nullable=False)  # INTEGER, STRING, BOOLEAN
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuditLog(Base):
    """Audit log model for tracking changes"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_type = Column(String(20), nullable=False)  # main_admin, staff
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    old_values = Column(Text, nullable=True)
    new_values = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())