"""
Database initialization and sample data creation
"""

import os
from sqlalchemy.orm import Session
from backend.database.database import engine, SessionLocal, Base
from backend.database.models import *
from backend.utils.security import hash_password
from datetime import time

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Create main admin if not exists
        admin = db.query(MainAdmin).filter(MainAdmin.email == "admin@srmist.edu.in").first()
        if not admin:
            admin = MainAdmin(
                email="admin@srmist.edu.in",
                password_hash=hash_password("admin123"),
                name="Main Administrator"
            )
            db.add(admin)
            db.commit()
            print("✅ Created main admin account")
        
        # Create sample departments
        departments_data = [
            {"name": "Computer Science Engineering", "code": "CSE"},
            {"name": "Information Technology", "code": "IT"},
            {"name": "Electronics and Communication", "code": "ECE"},
            {"name": "Mechanical Engineering", "code": "MECH"},
            {"name": "Civil Engineering", "code": "CIVIL"}
        ]
        
        for dept_data in departments_data:
            dept = db.query(Department).filter(Department.code == dept_data["code"]).first()
            if not dept:
                dept = Department(**dept_data)
                db.add(dept)
        
        db.commit()
        print("✅ Created sample departments")
        
        # Create time slots
        time_slots_data = [
            {"slot_name": "Slot 1", "start_time": time(9, 0), "end_time": time(10, 0)},
            {"slot_name": "Slot 2", "start_time": time(10, 0), "end_time": time(11, 0)},
            {"slot_name": "Slot 3", "start_time": time(11, 15), "end_time": time(12, 15)},
            {"slot_name": "Slot 4", "start_time": time(12, 15), "end_time": time(13, 15)},
            {"slot_name": "Slot 5", "start_time": time(14, 0), "end_time": time(15, 0)},
            {"slot_name": "Slot 6", "start_time": time(15, 0), "end_time": time(16, 0)},
            {"slot_name": "Slot 7", "start_time": time(16, 15), "end_time": time(17, 15)},
            {"slot_name": "Slot 8", "start_time": time(17, 15), "end_time": time(18, 15)}
        ]
        
        for slot_data in time_slots_data:
            slot = db.query(TimeSlot).filter(TimeSlot.slot_name == slot_data["slot_name"]).first()
            if not slot:
                slot = TimeSlot(**slot_data)
                db.add(slot)
        
        db.commit()
        print("✅ Created time slots")
        
        # Create sample classrooms
        cse_dept = db.query(Department).filter(Department.code == "CSE").first()
        if cse_dept:
            for i in range(1, 11):
                room = db.query(Classroom).filter(Classroom.room_number == f"CSE-{i:03d}").first()
                if not room:
                    room = Classroom(
                        room_number=f"CSE-{i:03d}",
                        capacity=60 if i <= 5 else 30,
                        room_type="Theory" if i <= 5 else "Lab",
                        department_id=cse_dept.id
                    )
                    db.add(room)
        
        db.commit()
        print("✅ Created sample classrooms")
        
        # Create system rules
        rules_data = [
            {"rule_name": "max_subjects_assistant_professor", "rule_value": "2", "rule_type": "INTEGER", "description": "Maximum subjects for Assistant Professor"},
            {"rule_name": "max_subjects_professor", "rule_value": "1", "rule_type": "INTEGER", "description": "Maximum subjects for Professor"},
            {"rule_name": "max_subjects_hod", "rule_value": "1", "rule_type": "INTEGER", "description": "Maximum subjects for HOD"},
            {"rule_name": "max_hours_per_day", "rule_value": "6", "rule_type": "INTEGER", "description": "Maximum teaching hours per day"},
            {"rule_name": "lunch_break_start", "rule_value": "13:15", "rule_type": "STRING", "description": "Lunch break start time"},
            {"rule_name": "lunch_break_end", "rule_value": "14:00", "rule_type": "STRING", "description": "Lunch break end time"}
        ]
        
        for rule_data in rules_data:
            rule = db.query(SystemRule).filter(SystemRule.rule_name == rule_data["rule_name"]).first()
            if not rule:
                rule = SystemRule(**rule_data)
                db.add(rule)
        
        db.commit()
        print("✅ Created system rules")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

def initialize_database():
    """Initialize database with tables and sample data"""
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    print("📊 Creating sample data...")
    create_sample_data()
    print("✅ Sample data created")

if __name__ == "__main__":
    initialize_database()