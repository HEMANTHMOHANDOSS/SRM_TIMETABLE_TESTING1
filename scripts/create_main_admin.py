# scripts/create_main_admin.py
from backend.database.database import SessionLocal
from backend.database.models import MainAdmin
from backend.utils.security import hash_password

db = SessionLocal()

admin_email = "admin@srmist.edu.in"
admin_password = "admin123"
existing = db.query(MainAdmin).filter(MainAdmin.email == admin_email).first()

if not existing:
    new_admin = MainAdmin(
        name="Super Admin",
        email=admin_email,
        password_hash=hash_password(admin_password)
    )
    db.add(new_admin)
    db.commit()
    print("✅ Admin created successfully")
else:
    print("⚠️ Admin already exists")

db.close()
