from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.projects import (
    CreateProject,  
    ProjectResponse,
    UpdateProject,
   
)
from app.dependencles.dependencles import get_current_user
from app.services.projects import (
    create_project_service, 
    get_project_service,
    get_project_by_id_service,
    delete_project_by_id_service,
    update_project_by_id_service,
)

router = APIRouter(prefix="/project", tags=['PROJECT'])

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Thêm dự án mới",
    description="Tạo một dự án mới. Người đăng nhập thực hiện hành động này sẽ tự động trở thành OWNER (Chủ sở hữu) của dự án."
)
def create_project(
    req: Request, 
    project: CreateProject, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    new_project = create_project_service(project, current_user, db)
    new_project_data = ProjectResponse.model_validate(new_project)
    return create_response(
        request=req,
        status_code=status.HTTP_201_CREATED, 
        message="Thêm dự án mới thành công!",
        data=new_project_data
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách dự án",
    description="Lấy danh sách toàn bộ các dự án mà người dùng hiện tại đang tham gia (với vai trò là OWNER hoặc MEMBER). Hỗ trợ tìm kiếm theo tên."
)
def get_project(
    req: Request,  
    search_project: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    result = get_project_service(search_project, current_user, db)
    result_data = [ProjectResponse.model_validate(r) for r in result]
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK, 
        message="Lấy danh sách dự án thành công!",
        data=result_data
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Lấy dự án theo ID",
    description="Xem chi tiết thông tin một dự án cụ thể theo ID. Chỉ thành viên của dự án mới có quyền xem."
)
def get_project_by_id(
    req: Request,  
    id: int,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    result = get_project_by_id_service(id, current_user, db)
    result_data = [ProjectResponse.model_validate(r) for r in result]
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK, 
        message="Lấy thông tin dự án thành công!",
        data=result_data
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa dự án (Xóa mềm)",
    description="Xóa dự án khỏi danh sách hoạt động mà không làm mất dữ liệu trong database (Soft Delete). Chỉ OWNER mới được thực hiện."
)
def delete_project(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    delete_project_by_id_service(id, current_user, db)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Xóa dự án thành công!",
        data=None
    )


@router.put(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Sửa thông tin dự án",
    description="Cập nhật tên hoặc mô tả của dự án. Chỉ OWNER mới được thực hiện."
)
def update_project(
    id: int,
    update_project: UpdateProject,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    project = update_project_by_id_service(id, update_project, current_user, db)
    project_data = ProjectResponse.model_validate(project)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Sửa dự án thành công!",
        data=project_data
    )


# # --- QUẢN LÝ THÀNH VIÊN DỰ ÁN ---

# @router.post(
#     "/{id}/members",
#     status_code=status.HTTP_201_CREATED,
#     summary="Thêm thành viên vào dự án",
#     description="Thêm một người dùng khác vào dự án với vai trò MEMBER hoặc OWNER. Chỉ OWNER hiện tại mới được thực hiện."
# )
# def add_member(
#     id: int,
#     new_member: CreateProjectMember,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user),
#     req: Request = None
# ):
#     member = add_user_in_project(id, new_member, current_user, db)
#     member_data = ProjectMemberResponse.model_validate(member)
#     return create_response(
#         request=req,
#         status_code=status.HTTP_201_CREATED,
#         message="Thêm thành viên vào dự án thành công!",
#         data=member_data
#     )


# @router.delete(
#     "/{id}/members/{user_id}",
#     status_code=status.HTTP_200_OK,
#     summary="Xóa thành viên khỏi dự án",
#     description="Xóa quyền truy cập của một thành viên khỏi dự án. Chỉ OWNER dự án mới được thực hiện. Không được xóa OWNER của dự án."
# )
# def remove_member(
#     id: int,
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user),
#     req: Request = None
# ):
#     delete_user_in_project(id, user_id, current_user, db)
#     return create_response(
#         request=req,
#         status_code=status.HTTP_200_OK,
#         message="Xóa thành viên khỏi dự án thành công!",
#         data=None
#     )


# @router.get(
#     "/{id}/members",
#     status_code=status.HTTP_200_OK,
#     summary="Lấy danh sách thành viên dự án",
#     description="Lấy danh sách toàn bộ thành viên và vai trò của họ trong dự án. Chỉ thành viên của dự án mới được xem."
# )
# def get_project_members(
#     id: int,
#     db: Session = Depends(get_db),
#     current_user = Depends(get_current_user),
#     req: Request = None
# ):
#     members = get_project_members_service(id, current_user, db)
#     members_data = [ProjectMemberDetailResponse.model_validate(m) for m in members]
#     return create_response(
#         request=req,
#         status_code=status.HTTP_200_OK,
#         message="Lấy danh sách thành viên dự án thành công!",
#         data=members_data
#     )
