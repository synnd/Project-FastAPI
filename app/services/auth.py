from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.users import CreateUser, UserLogin
from app.models.users import UserModel
from app.core.security import hash_password,verify_password,create_access_token

def create_user_service(new_user: CreateUser, db: Session):
    user_email = db.query(UserModel).filter(UserModel.email == new_user.email).first()
    if user_email:
        return None
    
    new_user_register = UserModel(
        email = new_user.email,
        full_name = new_user.full_name,
        password_hash = hash_password(new_user.password_hash)
    )
    
    db.add(new_user_register)
    db.commit()
    db.refresh(new_user_register)
    
    return new_user_register

def user_login_service(user : UserLogin, db: Session):
    user_db = db.query(UserModel).filter(UserModel.email == user.email).first()
    
    if not user_db or  not verify_password(user.password_hash, user_db.password_hash):
        return None

    return {
        'access_token': create_access_token({
            'id': user_db.id,
            'role': user_db.role,
            'email': user_db.email
        })
    }