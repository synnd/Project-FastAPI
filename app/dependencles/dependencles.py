from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from app.core.security import decode_access_token, TokenExpiredException, TokenInvalidException
from sqlalchemy.orm import Session
from app.models.users import UserModel
from app.database.database import get_db

security = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db),
    cred : HTTPAuthorizationCredentials = Depends(security),
):
    #  lấy token đã được lưu khi đăng nhập
    token = cred.credentials 
    try:
        #  giải mã token 
        payload = decode_access_token(token)
        
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ hoặc thiếu thông tin định danh"
            )
            
        # 3. Truy vấn Database để lấy trạng thái mới nhất
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Người dùng không tồn tại trong hệ thống"
            )
            
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tài khoản đã bị khóa"
            )
        return payload
    #  Lỗi khi Token hết hạn
    except TokenExpiredException as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))
    # Lối khi Token không hợp lệ
    except TokenInvalidException as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))


def get_current_admin(current_user= Depends(get_current_user)):
    role = current_user.get('role', '')
    if str(role).upper() != "ADMIN":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Quyền admin không hợp lệ')

    return current_user

    