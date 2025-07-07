from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import Staff, MainAdmin, Department
from backend.schemas.schemas import LoginRequest, LoginResponse, RegisterRequest
from backend.utils.security import (
    verify_password, hash_password, create_access_token, validate_email_domain
)
import jwt

router = APIRouter()

# JWT Config
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user_type = payload.get("user_type")

        if not user_id or not user_type:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user_id": user_id, "user_type": user_type}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    if not validate_email_domain(request.email):
        raise HTTPException(status_code=400, detail="Only SRM email addresses are allowed")

    user = None
    user_type = request.user_type.lower()

    if user_type == "main_admin":
        user = db.query(MainAdmin).filter(MainAdmin.email == request.email).first()
    elif user_type == "staff":
        user = db.query(Staff).filter(Staff.email == request.email).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(
        data={"user_id": user.id, "user_type": user_type}
    )

    user_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "user_type": user_type
    }

    if user_type == "staff":
        department = db.query(Department).filter(Department.id == user.department_id).first()
        user_data.update({
            "role": user.role,
            "department_id": user.department_id,
            "department_name": department.name if department else None,
            "is_department_admin": user.is_department_admin,
            "max_subjects": user.max_subjects
        })

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_data
    )

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if not validate_email_domain(request.email):
        raise HTTPException(status_code=400, detail="Only SRM email addresses are allowed")

    if db.query(Staff).filter(Staff.email == request.email).first() or \
       db.query(MainAdmin).filter(MainAdmin.email == request.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    department = db.query(Department).filter(Department.id == request.department_id).first()
    if not department:
        raise HTTPException(status_code=400, detail="Invalid department")

    max_subjects = 2 if request.role == "Assistant Professor" else 1

    staff = Staff(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role,
        department_id=request.department_id,
        max_subjects=max_subjects
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return {"message": "Registration successful", "staff_id": staff.id}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user
