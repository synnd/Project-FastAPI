from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.users import CreateUser, UserLogin
from app.models.users import UserModel
from app.core.security import hash_password,verify_password,create_access_token,create_refresh_token

def create_user_service(new_user: CreateUser, db: Session):
    user_email = db.query(UserModel).filter(UserModel.email == new_user.email).first()
    if user_email:
        return None
    
    full_name = new_user.full_name.strip().split(" ")
    
    if len(full_name) <2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,"Tên phải có ít nhất 2 từ")
    
    new_user_register = UserModel(
        email = new_user.email.lower().strip(),
        full_name = new_user.full_name,
        password_hash = hash_password(new_user.password_hash)
    )
    
    db.add(new_user_register)
    db.commit()
    db.refresh(new_user_register)
    
    return new_user_register

def user_login_service(user : UserLogin, db: Session):
    user_db = db.query(UserModel).filter(UserModel.email == user.email).first()
    
    if not user_db or not verify_password(user.password, user_db.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác"
        )
        
    if not user_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị khóa"
        )
        
    token_payload = {
        "email": user_db.email,
        "id": user_db.id,
        "role": user_db.role
    }
    
    return {
        'access_token': create_access_token(token_payload),
        'refresh_token': create_refresh_token(token_payload),
        "token_type": "bearer",
        "User": token_payload
    }
