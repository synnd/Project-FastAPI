from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session,joinedload
from app.models.projects import ProjectModel , ProjectMemberModel,MemberRole
from app.models.users import UserModel
from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.projects import CreateProject, UpdateProject, CreateProjectMember

def create_project_service(project: CreateProject, current_user: dict, db: Session):
    new_project = ProjectModel(
        name= project.name,
        description=project.description,
        owner_id=current_user['id']
    )
    db.add(new_project)
    # Đẩy xuống DB để lấy new_project.id mà chưa commit hoàn toàn
    db.flush()
    
    new_owner_member = ProjectMemberModel(
        project_id=new_project.id,
        user_id=current_user['id'],
        role=MemberRole.OWNER
    )
    db.add(new_owner_member)
    
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
              .filter(ProjectMemberModel.user_id == current_id)
              
    if search_name_project:
        query = query.filter(ProjectModel.name.ilike(f"%{search_name_project}%")).all()
        
    return query

def get_project_by_id_service(
    id : int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    query = db.query(ProjectModel)\
                .join(ProjectMemberModel, ProjectModel.id == ProjectMemberModel.project_id)\
                .filter(ProjectMemberModel.user_id == current_id)
                
    if id:
        query = query.filter(ProjectModel.id == id).all()
            
    return query

def delete_project_by_id_service(
    id : int,
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
            detail="Bạn không có quyền xóa dự án này"
        )
        
    db.delete(project)
    db.commit()
    
    return project

def update_project_by_id_service(
    id : int,
    update_project: UpdateProject,
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
            detail="Bạn không có quyền sửa dự án này"
        )
        
    for key, value in update_project.model_dump().items():
        setattr(project,key,value)

    db.commit()
    db.refresh(project)
    
    
    return update_project.model_dump()



