from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.users import CreateUser, UserResponse,UserLogin
from app.services.auth import create_user_service, user_login_service

router = APIRouter(prefix='/auth', tags=['AUTH'])

@router.post('/register')
def user_register(req : Request,new_user: CreateUser, db : Session = Depends(get_db)):
    user_register = create_user_service(new_user,db)
    if user_register is None:
        return create_response(request= req, status_code=status.HTTP_400_BAD_REQUEST,message="Email đã tồn tại",data=user_register)
    
    user_response_data = UserResponse.model_validate(user_register)
    return create_response(request= req,status_code= status.HTTP_201_CREATED,message="Tạo người dùng thành công!" , data=user_response_data)



@router.post('/login')
def user_login(req: Request,user: UserLogin, db: Session=Depends(get_db)):

    user_db = user_login_service(user,db)
    if user_db is None:
        return create_response(request= req, status_code=status.HTTP_400_BAD_REQUEST,message="Email hoặc mật khẩu không chính xác!",data=[])
    
    return create_response(request= req,status_code= status.HTTP_201_CREATED,message="Đăng nhập thành công!" , data= user_db)
