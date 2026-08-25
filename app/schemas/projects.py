from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.projects import MemberRole

class CreateProject(BaseModel):
    name: str = Field( ..., min_length=1, max_length=255, description="Tên của dự án" )
    description: Optional[str] = Field( default=None, description="Mô tả chi tiết về dự án" )
    
class UpdateProject(CreateProject):
    pass

class CreateProjectMember(BaseModel):
    user_id: int = Field(..., description="ID của người dùng cần thêm vào dự án")
    role: MemberRole = Field(default=MemberRole.MEMBER, description="Vai trò của thành viên trong dự án")

    
class ProjectResponse(BaseModel):
    id : int
    name : str
    description : Optional[str] = None
    owner_id : int
    created_at : datetime
    
    model_config = {
        "from_attributes": True
        }
    
class ProjectMemberResponse(BaseModel):
    project_id: int
    user_id: int
    role: MemberRole

    model_config = {
        "from_attributes": True
    }

class ProjectMemberDetailResponse(BaseModel):
    user_id: int
    email: str
    full_name: str
    role: MemberRole
    joined_at: datetime
    model_config = {
        "from_attributes": True
    }