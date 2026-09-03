from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.response import create_response
from app.dependencles.dependencles import get_current_admin
from app.services.admin import get_users_service
from app.schemas.users import UserResponse

router = APIRouter(prefix="/admin", tags=['ADMIN'])

@router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách người dùng toàn hệ thống",
    description="Lọc, tìm kiếm và lấy toàn bộ danh sách người dùng trong hệ thống. Chỉ tài khoản ADMIN mới có quyền truy cập."
)
def get_users(
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
    