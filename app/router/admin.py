from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.users import UserResponse
from app.dependencles.dependencles import get_current_user,get_current_admin
from app.services.admin import get_users_service

from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session
from typing import Optional



router= APIRouter(prefix="/admin", tags=['admin'])

@router.get('/')
def search_user(
    req: Request,
    name: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    limit: int = 10,
    current_admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users, total = get_users_service(db, name, email, is_active, page, limit)
    
    
    users_data = [UserResponse.model_validate(user) for user in users]
    
    response_data = {
        "users": users_data,
        "total": total,
        "page": page,
        "limit": limit
    }
    
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách người dùng thành công",
        data=response_data
    )

