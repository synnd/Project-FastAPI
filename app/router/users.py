from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.dependencles.dependencles import get_current_user
from app.services.users import get_info_user_service
from app.schemas.users import UserResponse

router = APIRouter(prefix="/user", tags=['USER'])

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Lấy thông tin tài khoản hiện tại",
    description="Giải mã access token và truy vấn lấy thông tin hồ sơ mới nhất của người dùng từ cơ sở dữ liệu."
)
def get_info_user(req: Request, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    user_db = get_info_user_service(current_user, db)
    user_response = UserResponse.model_validate(user_db)
    return create_response(request=req, status_code=status.HTTP_200_OK, message="Thông tin user", data=user_response)