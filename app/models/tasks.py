from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
import enum
from app.database.database import Base

class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True) 
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False) 
    title = Column(String(255), nullable=False) 
    description = Column(Text, nullable=True) 
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Người được giao
    
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False) 
    due_date = Column(DateTime, nullable=True) # Hạn xử lý
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Quan hệ
    project = relationship("ProjectModel", back_populates="tasks")
    assignee = relationship("UserModel", back_populates="tasks")
    comments = relationship("CommentModel", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("AttachmentModel", back_populates="task", cascade="all, delete-orphan")


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Quan hệ
    task = relationship("TaskModel", back_populates="comments")
    user = relationship("UserModel")


class AttachmentModel(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)

    # Quan hệ
    task = relationship("TaskModel", back_populates="attachments")
    user = relationship("UserModel")