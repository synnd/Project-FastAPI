from fastapi import APIRouter, Depends, HTTPException,status,Request
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.response import create_response
from app.schemas.projects import CreateProject,  ProjectResponse,UpdateProject,CreateProjectMember,ProjectMemberResponse
from app.dependencles.dependencles import get_current_user
from app.services.projects import (create_project_service, 
                                   get_project_service,
                                   get_project_by_id_service,
                                   delete_project_by_id_service,
                                   update_project_by_id_service,
                                   )

router = APIRouter(prefix="/project",tags=['PROJECT'])

# Thêm dự án mới
@router.post("/")
def create_project(
    req: Request, 
    project: CreateProject, 
    db: Session=Depends(get_db), 
    current_user = Depends(get_current_user)
):
    new_project = create_project_service(project, current_user, db)

    new_project = ProjectResponse.model_validate(new_project)
    return create_response(request=req,status_code=status.HTTP_201_CREATED, message="Thêm dự án mới thành công!",data=new_project)

#  Lấy thông tin dự án
@router.get("/")
def get_project(
    req:Request,  
    search_project: str,
    db: Session=Depends(get_db), 
    current_user = Depends(get_current_user)
    ):
    result = get_project_service(search_project,current_user, db)
   
        
    result = [ProjectResponse.model_validate(r) for r in result]
    
    return create_response(request=req,status_code=status.HTTP_200_OK, message="Danh sách dự án !",data=result)


# Lấy dự án theo ID
@router.get("/{id}")
def get_project_by_id(
    req:Request,  
    id: int,
    db: Session=Depends(get_db), 
    current_user = Depends(get_current_user)
    ):
    result = get_project_by_id_service(id,current_user, db)
       
            
    result = [ProjectResponse.model_validate(r) for r in result]
    return create_response(request=req,status_code=status.HTTP_200_OK, message="Danh sách dự án !",data=result)


#  Xóa dự án theo ID : chỉ owner được xóa
@router.delete("/{id}")
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
    

# Sửa dự án theo ID : chỉ owner được sửa
@router.put("/{id}")
def update_project(
    id: int,
    update_project : UpdateProject,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    project=  update_project_by_id_service(id,update_project ,current_user, db)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Sửa dự án thành công!",
        data= project
    )
    
