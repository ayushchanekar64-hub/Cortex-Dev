from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from ..database import get_db
from ..models import User
import hashlib
import secrets
import datetime

router = APIRouter(prefix="/auth", tags=["auth"])

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_reset_token():
    return secrets.token_urlsafe(32)

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user": {"id": new_user.id, "username": new_user.username}}

@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.email == user.username_or_email) | (User.username == user.username_or_email)).first()
    if not db_user or db_user.hashed_password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "user": {"id": db_user.id, "username": db_user.username}}

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == request.email).first()
    if not db_user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = generate_reset_token()
    reset_token_expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    
    # Store token in user record (you might want a separate table for this in production)
    db_user.reset_token = reset_token
    db_user.reset_token_expiry = reset_token_expiry
    db.commit()
    
    # In a real implementation, you would send an email here
    # For demo purposes, we'll return the reset link in the response
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    
    return {
        "message": "Password reset link sent to email",
        "reset_link": reset_link,  # Remove this in production
        "token": reset_token  # Remove this in production
    }

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.reset_token == request.token).first()
    
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check if token is expired
    if db_user.reset_token_expiry and db_user.reset_token_expiry < datetime.datetime.now(datetime.timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password
    db_user.hashed_password = hash_password(request.new_password)
    db_user.reset_token = None
    db_user.reset_token_expiry = None
    db.commit()
    
    return {"message": "Password reset successfully"}
