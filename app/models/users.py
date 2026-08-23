from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from sqlalchemy.orm import relationship
import enum
from app.database.database import Base 

# Định nghĩa kiểu ENUM cho Role
class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False) 
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False) 
    is_active = Column(Boolean, default=True) 
    created_at = Column(DateTime, default=func.now())

    # Quan hệ 
    owned_projects = relationship("ProjectModel", back_populates="owner") 
    tasks = relationship("TaskModel", back_populates="assignee")
    project_memberships = relationship("ProjectMemberModel", back_populates="user")