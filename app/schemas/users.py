from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.users import UserRole

class CreateUser(BaseModel):
    email : EmailStr = Field(..., description="Email đăng nhập hợp lệ")
    full_name :str = Field(..., min_length=3, max_length=50, description="Họ và tên người dùng" )
    password_hash :str = Field(..., min_length=6, max_length=30, description="Nhập mật khẩu của bạn")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email đăng nhập hợp lệ")
    password: str = Field(..., min_length=6, max_length=30, description="Mật khẩu đăng nhập")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

