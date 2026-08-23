from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session
from app.models.users import UserModel
from app.schemas.response import create_response

def get_info_user_service(current_user :dict ,db: Session):

    
    user = db.query(UserModel).filter(UserModel.email == current_user.get('email')).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Người dùng không tồn tại"
        )
        
    # Kiểm tra nếu tài khoản bị khóa
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị khóa"
        )
        
    return user
    