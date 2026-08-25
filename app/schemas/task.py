from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.tasks import TaskPriority, TaskStatus

class CreateTask(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Tiêu đề task")
    description: Optional[str] = Field(default=None, description="Mô tả chi tiết")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Độ ưu tiên: LOW, MEDIUM, HIGH")
    assignee_id: Optional[int] = Field(default=None, description="ID người được giao việc")
    due_date: Optional[datetime] = Field(default=None, description="Thời hạn hoàn thành")
    


class UpdateTask(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255, description="Tiêu đề task")
    description: Optional[str] = Field(default=None, description="Mô tả chi tiết")
    priority: Optional[TaskPriority] = Field(default=None, description="Độ ưu tiên")
    status: Optional[TaskStatus] = Field(default=None, description="Trạng thái công việc")
    assignee_id: Optional[int] = Field(default=None, description="ID người được giao")
    due_date: Optional[datetime] = Field(default=None, description="Hạn hoàn thành")
    
    
class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class CreateComment(BaseModel):
    content: str = Field(..., min_length=1, description="Nội dung bình luận")

class CommentResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    full_name: str
    email: str
    content: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class AttachmentResponse(BaseModel):
    id: int
    task_id: int
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }


    