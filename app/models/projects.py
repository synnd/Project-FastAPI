from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from app.database.database import Base

class MemberRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True) 
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True) 
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Người sở hữu
    created_at = Column(DateTime, default=func.now(), nullable=False) 

    # Quan hệ
    owner = relationship("UserModel", back_populates="owned_projects") #người sở hữu 
    members = relationship("ProjectMemberModel", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("TaskModel", back_populates="project", cascade="all, delete-orphan")


#  thiết lập quan hệ N-N với user

class ProjectMemberModel(Base):
    __tablename__ = "project_members"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True) 
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True) 
    role = Column(Enum(MemberRole), nullable=False) 
    joined_at = Column(DateTime, default=func.now(), nullable=False) 

    # Quan hệ
    project = relationship("ProjectModel", back_populates="members")
    user = relationship("UserModel", back_populates="project_memberships")