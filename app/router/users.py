from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.users import UserResponse
from app.dependencles.dependencles import get_current_user
from app.services.users import get_info_user_service


router= APIRouter(prefix="/user", tags=['USER'])

@router.get("/me")
def get_info_user(req:Request, current_user = Depends(get_current_user),db: Session=Depends(get_db)):
    user_db = get_info_user_service(current_user, db)
    
    user_response_data = UserResponse.model_validate(user_db)
    
    return create_response(
        request=req, 
        status_code=status.HTTP_200_OK, 
        message="Lấy thông tin người dùng thành công", 
        data=user_response_data
    )