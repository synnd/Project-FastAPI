from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session,joinedload
from app.models.projects import ProjectModel , ProjectMemberModel,MemberRole
from app.models.users import UserModel
from app.schemas.response import create_response
from app.schemas.projects import CreateProject, UpdateProject, CreateProjectMember


# Thêm user vào sự án(chỉ owner được thêm
def add_user_in_project(
    id: int,
    new_member : CreateProjectMember,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
        
    # 1. Tìm dự án theo ID
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
        
    # 2. Kiểm tra quyền OWNER
    if project.owner_id != current_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thêm thành viên mới"
        )
    # 3 kiểm tra người dùng có tồn tại trong hệ thống
    user_to_add = db.query(UserModel).filter(UserModel.id == new_member.user_id).first()
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Người dùng cần thêm không tồn tại trong hệ thống"
        )
        
    # 4. Kiểm tra user_id đã tồn tại trong dự án chưa 
    existing_member = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == project.id,
        ProjectMemberModel.user_id == new_member.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng này đã tham gia dự án rồi"
        )
    
    new_member_create = ProjectMemberModel(
        project_id = project.id,
        user_id = new_member.user_id,
        role = new_member.role
    )
    
    db.add(new_member_create)
    db.commit()
    db.refresh(new_member_create)
    
    return new_member_create 

def delete_user_in_project(
    id: int,
    user_id: int,
    current_user: dict,
    db: Session
):  
    current_id = current_user['id']
            
    # 1. Tìm dự án theo ID
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
        
    # 2. Kiểm tra quyền OWNER
    if project.owner_id != current_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa thành viên"
        )
    # 3. Kiểm tra user_id có trong dự án không
    existing_member = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == id,
        ProjectMemberModel.user_id == user_id
    ).first()
    if not existing_member: 
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Không tìm thấy thành viên trong dự án"
                )
    # 4. Không cho xóa người sở hữu dự án
    if existing_member.user_id == project.owner_id :
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa người sở hữu dự án"
        )
        
    db.delete(existing_member)
    db.commit()
    
    return existing_member

# Trả danh sách member và role trong dự án
def get_project_members_service(
    id: int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    # 1. Tìm dự án
    project = db.query(ProjectModel).filter(ProjectModel.id == id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
        
    # 2. Kiểm tra xem người yêu cầu có thuộc dự án này không (Owner hoặc Member)
    user_membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == id,
        ProjectMemberModel.user_id == current_id
    ).first()
    
    if not user_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem danh sách thành viên của dự án này"
        )
        
    # 3. Lấy toàn bộ thành viên và liên kết với bảng User để lấy tên/email
    members = db.query(ProjectMemberModel)\
                .options(joinedload(ProjectMemberModel.user))\
                .filter(ProjectMemberModel.project_id == id)\
                .all()
                
    # 4. Sắp xếp danh sách thành viên: OWNER lên đầu, các vai trò khác ở sau
    members_sorted = sorted(members, key=lambda m: 0 if m.role == MemberRole.OWNER else 1)
                 
    # 5. Làm phẳng cấu trúc dữ liệu trả về
    result = [
        {
            "user_id": m.user.id,
            "email": m.user.email,
            "full_name": m.user.full_name,
            "role": m.role,
            "joined_at": m.joined_at
        }
        for m in members_sorted
    ]
    
    return result