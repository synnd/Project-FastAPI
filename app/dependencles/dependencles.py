from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from app.core.security import decode_access_token, TokenExpiredException, TokenInvalidException

security = HTTPBearer()

def get_current_user(
    cred : HTTPAuthorizationCredentials = Depends(security)
):
    #  lấy token đã được lưu khi đăng nhập
    token = cred.credentials 
    try:
        #  giải mã token 
        payload = decode_access_token(token)
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

    