import jwt 
import bcrypt
from datetime import datetime, timedelta, timezone
from app.core.config import SECRET_KEY, ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str):
     return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    # Tính toán thời gian hết hạn (exp)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    })
    
    return jwt.encode(
        payload= to_encode,
        key= SECRET_KEY,
        algorithm=ALGORITHM
    )


class TokenExpiredException(Exception):
    """Lỗi xảy ra khi token đã hết hạn sử dụng"""
    pass

class TokenInvalidException(Exception):
    """Lỗi xảy ra khi token không đúng định dạng hoặc sai chữ ký"""
    pass

def decode_access_token(token: str):
    try : 
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException("Token đã hết hạn, vui lòng đăng nhập lại")
    except jwt.InvalidTokenError:
        raise TokenInvalidException("Token không hợp lệ hoặc đã bị chỉnh sửa")