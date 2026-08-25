from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.users import CreateUser, UserResponse, UserLogin, TokenResponse
from app.services.auth import create_user_service, user_login_service
from app.core.security import decode_access_token, create_access_token, TokenExpiredException, TokenInvalidException

router = APIRouter(prefix='/auth', tags=['AUTH'])

@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản người dùng mới",
    description="Cho phép bất kỳ khách truy cập nào đăng ký tài khoản mới trong hệ thống. Email không được trùng lặp."
)
def user_register(req : Request, new_user: CreateUser, db : Session = Depends(get_db)):
    user_register = create_user_service(new_user, db)
    if user_register is None:
        return create_response(request=req, status_code=status.HTTP_400_BAD_REQUEST, message="Email đã tồn tại", data=None)
    
    user_response_data = UserResponse.model_validate(user_register)
    return create_response(request=req, status_code=status.HTTP_201_CREATED, message="Tạo người dùng thành công!", data=user_response_data)


@router.post('/login',
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập tài khoản",
    description="Xác thực Email và Mật khẩu, trả về cặp Access Token (hạn 30 phút) và Refresh Token (hạn 7 ngày)."
)
def user_login(req: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    
    data = user_login_service(login_data, db)
    return create_response(request=req, status_code=status.HTTP_201_CREATED, message="Tạo người dùng thành công!", data=data)


@router.post(
    '/refresh',
    summary="Làm mới Access Token",
    description="Gửi Refresh Token để nhận lại Access Token mới khi token cũ hết hạn."
)
def refresh_access_token(refresh_token: str = Query(..., description="Refresh Token hợp lệ")):
    try:
        payload = decode_access_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token này không phải là Refresh Token hợp lệ"
            )
            
        new_payload = payload.copy()
        new_payload.pop("exp", None)
        new_payload.pop("iat", None)
        new_payload.pop("type", None)
        
        new_access_token = create_access_token(data=new_payload)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token đã hết hạn, vui lòng đăng nhập lại"
        )
    except TokenInvalidException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh Token không hợp lệ"
        )
