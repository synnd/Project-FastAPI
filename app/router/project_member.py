from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.projects import CreateProject,  ProjectResponse,UpdateProject,CreateProjectMember,ProjectMemberResponse,ProjectMemberDetailResponse
from app.dependencles.dependencles import get_current_user
from app.services.project_member import add_user_in_project, delete_user_in_project,get_project_members_service
router = APIRouter(prefix="/project_member", tags=['PROJECT_MEMBER'])

#  Thêm thành viên vào dự án
@router.post("/{project_id}/members",summary= "Thêm thành viên vào dự án", description="Thêm thành viên the ID. Chỉ OWNER được thêm thành viên")
def add_member(
    project_id: int,
    new_member: CreateProjectMember,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    member = add_user_in_project(project_id, new_member, current_user, db)
    member_response = ProjectMemberResponse.model_validate(member)
    return create_response(
        request=req,
        status_code=status.HTTP_201_CREATED,
        message="Thêm thành viên vào dự án thành công!",
        data= member_response
    )


# Xóa thành viên theo ID

@router.delete("/{project_id}/members/{user_id}",summary="Xóa thành viên trong dự án",description="Xóa thành viên the ID. Chỉ OWNER được xóa thành viên")
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    delete_user_in_project(project_id, user_id, current_user, db)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message=f"Xóa thành viên {user_id} khỏi dự án thành công!",
        data=None
    )
    
# Xem danh sách thành viên
@router.get("/{project_id}/all_members",summary="Xem danh sách thành viên", description="Chỉ thành viên trong dự án mới được xem")
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    members = get_project_members_service(project_id, current_user, db)
    
    members_data = [ProjectMemberDetailResponse.model_validate(m) for m in members]
    
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách thành viên dự án thành công!",
        data=members_data
    )