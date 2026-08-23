from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.projects import CreateProject,  ProjectResponse,UpdateProject,CreateProjectMember,ProjectMemberResponse,ProjectMemberDetailResponse
from app.dependencles.dependencles import get_current_user
from app.services.project_member import add_user_in_project, delete_user_in_project,get_project_members_service
router = APIRouter(prefix="/project_member", tags=['PROJECT_MEMBER'])

#  Thêm thành viên vào dự án
@router.post("/{id}/members")
def add_member(
    id: int,
    new_member: CreateProjectMember,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    member = add_user_in_project(id, new_member, current_user, db)
    member_response = ProjectMemberResponse.model_validate(member)
    return create_response(
        request=req,
        status_code=status.HTTP_201_CREATED,
        message="Thêm thành viên vào dự án thành công!",
        data= member_response
    )


# Xóa thành viên theo ID

@router.delete("/{id}/members/{user_id}")
def remove_member(
    id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    delete_user_in_project(id, user_id, current_user, db)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message=f"Xóa thành viên {user_id} khỏi dự án thành công!",
        data=None
    )
    
# Xem danh sách thành viên
@router.get("/{id}/all_members")
def get_project_members(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    members = get_project_members_service(id, current_user, db)
    
    members_data = [ProjectMemberDetailResponse.model_validate(m) for m in members]
    
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách thành viên dự án thành công!",
        data=members_data
    )