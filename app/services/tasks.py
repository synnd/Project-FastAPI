from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload
from app.models.projects import ProjectModel, ProjectMemberModel, MemberRole
from app.models.users import UserModel
from app.models.tasks import TaskModel, TaskPriority, TaskStatus, CommentModel, AttachmentModel
from app.schemas.task import CreateTask, CreateComment, UpdateTask

# Tạo task mới
def create_task_service(
    project_id: int,  
    task: CreateTask,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
        
    # 1. Tìm dự án theo ID
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
        
    # 2. Kiểm tra xem người đang đăng nhập có thuộc dự án này không
    user_membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == project.id,
        ProjectMemberModel.user_id == current_id
    ).first()
    
    if not user_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của dự án này"
        )
        
    # 3. Kiểm tra quyền giao việc
    if task.assignee_id is not None:
        
        # Nếu người thực hiện là Member và giao việc cho người khác
        if project.owner_id != current_id and task.assignee_id != current_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chỉ OWNER mới có quyền giao task cho thành viên khác"
            )
            
        # Kiểm tra xem người được giao việc thuộc dự án không
        assignee_membership = db.query(ProjectMemberModel).filter(
            ProjectMemberModel.project_id == project.id,
            ProjectMemberModel.user_id == task.assignee_id
        ).first()
        
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao việc không phải là thành viên của dự án"
            )
            
    new_task = TaskModel(
        project_id=project.id, 
        title=task.title,
        description=task.description,
        priority=task.priority,
        assignee_id=task.assignee_id,
        due_date=task.due_date
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Lấy danh sách task (chỉ thành viên trong dự án)
def get_project_tasks_service(
    project_id: int,
    current_user: dict,
    db: Session,
    status_project: TaskStatus = None,
    priority: TaskPriority = None,
    assignee_id: int = None,
    search: str = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    current_id = current_user['id']
    
    # 1. Kiểm tra xem user hiện tại có thuộc dự án không
    membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == project_id,
        ProjectMemberModel.user_id == current_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem công việc của dự án này"
        )
        
    # 2. Tìm project
    query = db.query(TaskModel).filter(TaskModel.project_id == project_id)
    
    # 3. Lọc theo trạng thái (status)
    if status_project:
        query = query.filter(TaskModel.status == status)
        
    # 4. Lọc theo độ ưu tiên (priority)
    if priority:
        query = query.filter(TaskModel.priority == priority)
        
    # 5. Lọc theo người được giao (assignee_id)
    if assignee_id is not None:
        query = query.filter(TaskModel.assignee_id == assignee_id)
        
    # 6. Tìm kiếm theo tiêu đề (search title)
    if search:
        query = query.filter(TaskModel.title.ilike(f"%{search}%"))
        
    # 7. Sắp xếp (Sorting)
    sort_column = TaskModel.created_at
    if sort_by == "due_date":
        sort_column = TaskModel.due_date
        
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
        
    # 8. Phân trang (Pagination)
    total = query.count()
    offset = (page - 1) * limit
    tasks = query.offset(offset).limit(limit).all()
    
    return tasks, total


# Lấy task theo ID, chỉ thành viên trong dự án
def get_task_by_id_service(
    id: int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    # 1. Tìm kiếm Task theo ID
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc"
        )
        
    # 2. Kiểm tra xem người yêu cầu có thuộc dự án chứa Task này không
    membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == task.project_id,
        ProjectMemberModel.user_id == current_id
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xem chi tiết công việc này"
        )
        
    return task

# Cập nhật task

def update_task_service(
    id: int,
    task_update: UpdateTask,      
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    # 1. Tìm kiếm Task
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc"
        )
        
    # 2. Tìm Project chứa Task đó
    project = db.query(ProjectModel).filter(ProjectModel.id == task.project_id).first()
    
    # 3. Kiểm tra xem người thực hiện có thuộc dự án không
    user_membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == project.id,
        ProjectMemberModel.user_id == current_id
    ).first()
    
    if not user_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không phải là thành viên của dự án này"
        )
    # 4 .Phân quyền chỉnh sửa
    if project.owner_id != current_id and task.assignee_id != current_id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền sửa task này, chỉ OWNER và thành viên được giao task mới có quyền sửa"
            )
        
      
    # 5. Trích xuất các trường được truyền lên (loại bỏ các trường không được gửi)
    update_data = task_update.model_dump(exclude_unset=True) 
    
    if not update_data:
        return task 

    #  quyền owner
    is_owner = (project.owner_id == current_id)

    
    # 6. Nếu là MEMBER, không được phép thay đổi người nhận task
    if not is_owner and "assignee_id" in update_data:
        new_assignee = update_data["assignee_id"]
        
        if new_assignee != current_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Thành viên không được phép thay đổi người nhận task"
            )
        
    # 7. KIỂM TRA HỢP LỆ (Chỉ dành cho Owner): Khi giao task cho người khác, check xem người đó có trong dự án không
    if "assignee_id" in update_data and update_data["assignee_id"] is not None:
        
        assignee_id = update_data["assignee_id"]
        assignee_membership = db.query(ProjectMemberModel).filter(
            ProjectMemberModel.project_id == project.id,
            ProjectMemberModel.user_id == assignee_id
        ).first()
        
        if not assignee_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người được giao việc mới phải là thành viên của dự án"
            )
            
    # 8. Tiến hành cập nhật vào DB
    for key, value in update_data.items():
        setattr(task, key, value)
        
    db.commit()
    db.refresh(task)
    
    return task


# Xóa task: chỉ owner được xóa
def delete_task_service(
    id: int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    task = db.query(TaskModel).filter(TaskModel.id == id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy công việc"
        )
        
    project = db.query(ProjectModel).filter(ProjectModel.id == task.project_id).first()
    
    if project.owner_id != current_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền xóa task này. Chỉ OWNER mới được xóa task"
        )
        
    db.delete(task)
    db.commit()
    
    return task


# Thêm bình luận cho task
def add_comment_to_task_service(
    task_id: int,
    comment_in: CreateComment,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy công việc")
        
    membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == task.project_id,
        ProjectMemberModel.user_id == current_id
    ).first()
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bạn không thuộc dự án này")
        
    new_comment = CommentModel(
        task_id=task_id,
        user_id=current_id,
        content=comment_in.content
    )
    
    user = db.query(UserModel).filter(UserModel.id == current_id).first()
    
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return  
# Xem bình luận
def get_task_comments_service(
    task_id: int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy công việc")
        
    membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == task.project_id,
        ProjectMemberModel.user_id == current_id
    ).first()
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bạn không thuộc dự án này")
        
    comments = db.query(CommentModel)\
                 .options(joinedload(CommentModel.user))\
                 .filter(CommentModel.task_id == task_id)\
                 .order_by(CommentModel.created_at.asc())\
                 .all()
                 
    result = [
        {
            "id": c.id,
            "task_id": c.task_id,
            "user_id": c.user_id,
            "full_name": c.user.full_name,
            "email": c.user.email,
            "content": c.content,
            "created_at": c.created_at
        }
        for c in comments
    ]
    return result


# Đính kèm File
def upload_task_attachment_service(
    task_id: int,
    file_name: str,
    file_path: str,
    file_size: int,
    mime_type: str,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy công việc")
        
    membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == task.project_id,
        ProjectMemberModel.user_id == current_id
    ).first()
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bạn không thuộc dự án này")
        
    attachment = AttachmentModel(
        task_id=task_id,
        user_id=current_id,
        file_name=file_name,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


# Xem danh sách File đính kèm
def get_task_attachments_service(
    task_id: int,
    current_user: dict,
    db: Session
):
    current_id = current_user['id']
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Không tìm thấy công việc")
        
    membership = db.query(ProjectMemberModel).filter(
        ProjectMemberModel.project_id == task.project_id,
        ProjectMemberModel.user_id == current_id
    ).first()
    if not membership:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bạn không thuộc dự án này")
        
    attachments = db.query(AttachmentModel).filter(AttachmentModel.task_id == task_id).all()
    return attachments
