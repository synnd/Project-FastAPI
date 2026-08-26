from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.models.projects import ProjectModel, ProjectMemberModel, MemberRole
from app.models.users import UserModel
from app.models.activity_log import ActivityLogModel
from app.schemas.projects import CreateProject, CreateProjectMember, UpdateProject

def log_activity(db: Session, user_id: int, action: str, project_id: int, details: str):
    log_entry = ActivityLogModel(
        user_id=user_id,
        action=action,
        project_id=project_id,
        details=details
    )
    db.add(log_entry)
    db.flush()

def create_project_service(project: CreateProject, current_user: dict, db: Session):
    current_id = current_user['id']
    new_project = ProjectModel(
        name= project.name,
        description=project.description,
        owner_id=current_id
    )
    db.add(new_project)
    db.flush()
    
    new_owner_member = ProjectMemberModel(
        project_id=new_project.id,
        user_id=current_id,
        role=MemberRole.OWNER
    )
    db.add(new_owner_member)
    
    log_activity(db, current_id, "CREATE_PROJECT", new_project.id, f"Đã tạo dự án '{new_project.name}'")
    
    db.commit()
    db.refresh(new_project)
    
    return new_project


def get_project_service(
    search_name_project : str,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    query = db.query(ProjectModel)\
              .join(ProjectMemberModel, ProjectModel.id == ProjectMemberModel.project_id)\
              .filter(ProjectMemberModel.user_id == current_id)\
              .filter(ProjectModel.is_deleted == False)
              
    if search_name_project:
        query = query.filter(ProjectModel.name.ilike(f"%{search_name_project}%"))
        
    return query.all()

def get_project_by_id_service(
    id : int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    query = db.query(ProjectModel)\
              .join(ProjectMemberModel, ProjectModel.id == ProjectMemberModel.project_id)\
              .filter(ProjectMemberModel.user_id == current_id)\
              .filter(ProjectModel.is_deleted == False)
                      
    # 2. Lấy dự án theo ID cụ thể
    project = query.filter(ProjectModel.id == id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy dự án hoặc bạn không có quyền truy cập"
        )
            
    return project

def delete_project_by_id_service(id : int, current_user: dict, db: Session):
    current_id = current_user['id']
    
    project = db.query(ProjectModel).filter(ProjectModel.id == id, ProjectModel.is_deleted == False).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án")
        
    if project.owner_id != current_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền xóa dự án này")
        
    project.is_deleted = True
    project.deleted_at = datetime.now()
    
    log_activity(db, current_id, "DELETE_PROJECT", project.id, f"Đã xóa dự án '{project.name}' (Xóa mềm)")
    
    db.commit()
    return project

def update_project_by_id_service(
    id : int,
    update_project: UpdateProject,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    project = db.query(ProjectModel).filter(ProjectModel.id == id, ProjectModel.is_deleted == False).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dự án")
        
    if project.owner_id != current_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền sửa dự án này")
        
    for key, value in update_project.model_dump().items():
        setattr(project, key, value)
        
    log_activity(db, current_id, "UPDATE_PROJECT", project.id, f"Đã cập nhật thông tin dự án '{project.name}'")
    
    db.commit()
    db.refresh(project)
    
    return project




