import os
import uuid
from fastapi import APIRouter, Depends, status, Request, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import get_db
from app.schemas.response import create_response
from app.dependencles.dependencles import get_current_user
from app.schemas.task import (
    CreateTask, 
    TaskResponse, 
    CreateComment, 
    CommentResponse, 
    AttachmentResponse,
    UpdateTask
)
from app.models.tasks import TaskPriority, TaskStatus
from app.services.tasks import (
    create_task_service,
    get_project_tasks_service,
    get_task_by_id_service,
    update_task_service,
    delete_task_service,
    add_comment_to_task_service,
    get_task_comments_service,
    upload_task_attachment_service,
    get_task_attachments_service
)

router = APIRouter(prefix='/task', tags=['TASK'])

@router.post(
    '/project/{id}',
    status_code=status.HTTP_201_CREATED,
    summary="Tạo công việc (Task) mới cho dự án",
    description="Tạo một task mới thuộc dự án. Owner có quyền giao việc cho bất kỳ ai, Member chỉ có thể tự giao cho mình hoặc để trống."
)
def create_task(
    id: int, # project_id
    task: CreateTask,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    req: Request = None
):
    new_task = create_task_service(id, task, current_user, db)
    task_data = TaskResponse.model_validate(new_task)
    return create_response(
        request=req,
        status_code=status.HTTP_201_CREATED,
        message="Tạo công việc thành công!",
        data=task_data
    )


@router.get(
    '/project/{id}',
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách công việc của dự án",
    description="Lấy danh sách công việc thuộc một dự án cụ thể. Hỗ trợ lọc theo trạng thái, độ ưu tiên, người được giao, tìm kiếm theo tiêu đề, sắp xếp và phân trang."
)
def get_project_tasks(
    id: int, # project_id
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    tasks, total = get_project_tasks_service(
        project_id=id,
        current_user=current_user,
        db=db,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    tasks_data = [TaskResponse.model_validate(task) for task in tasks]
    
    response_data = {
        "tasks": tasks_data,
        "total": total,
        "page": page,
        "limit": limit
    }
    
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách công việc thành công!",
        data=response_data
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Xem chi tiết công việc",
    description="Lấy thông tin chi tiết một công việc cụ thể theo ID. Chỉ thành viên dự án mới được xem."
)
def get_task_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    task = get_task_by_id_service(id, current_user, db)
    task_data = TaskResponse.model_validate(task)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy chi tiết công việc thành công!",
        data=task_data
    )


@router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Cập nhật công việc từng phần",
    description="Cập nhật thông tin công việc. Chỉ OWNER có toàn quyền, MEMBER chỉ được đổi trạng thái (status). Những trường không gửi lên sẽ không bị ghi đè."
)
def update_task(
    id: int,
    task_update: UpdateTask,  
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    task = update_task_service(id, task_update, current_user, db)
    task_data = TaskResponse.model_validate(task)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Cập nhật công việc thành công!",
        data=task_data
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Xóa công việc",
    description="Xóa vĩnh viễn công việc khỏi dự án. Chỉ OWNER dự án mới có quyền xóa."
)
def delete_task(
    id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    delete_task_service(id, current_user, db)
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Xóa công việc thành công!",
        data=None
    )


# --- QUẢN LÝ BÌNH LUẬN ---

@router.post(
    "/{id}/comments",
    status_code=status.HTTP_201_CREATED,
    summary="Viết bình luận cho công việc",
    description="Đăng một bình luận mới lên công việc. Chỉ thành viên dự án mới được thực hiện."
)
def add_comment(
    id: int, # task_id
    comment_in: CreateComment,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    comment = add_comment_to_task_service(id, comment_in, current_user, db)
    comment_data = CommentResponse.model_validate(comment)
    return create_response(
        request=req,
        status_code=status.HTTP_201_CREATED,
        message="Đăng bình luận thành công!",
        data=comment_data
    )


@router.get(
    "/{id}/comments",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách bình luận",
    description="Lấy toàn bộ danh sách các bình luận của một công việc cụ thể. Sắp xếp theo thời gian tăng dần."
)
def get_comments(
    id: int, # task_id
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    comments = get_task_comments_service(id, current_user, db)
    comments_data = [CommentResponse.model_validate(c) for c in comments]
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách bình luận thành công!",
        data=comments_data
    )


# --- QUẢN LÝ FILE ĐÍNH KÈM ---

@router.post(
    "/{id}/attachments",
    status_code=status.HTTP_201_CREATED,
    summary="Tải lên tệp đính kèm",
    description="Tải lên một tệp đính kèm liên kết tới công việc. Kích thước tối đa 5MB. Chỉ cho phép các định dạng: PDF, DOCX, DOC, PNG, JPG, JPEG, ZIP, RAR, TXT."
)
def upload_attachment(
    id: int, # task_id
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
    
    # Đo kích thước file
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kích thước tệp vượt quá giới hạn 5MB"
        )
        
    allowed_extensions = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".zip", ".rar", ".txt"}
    _, file_ext = os.path.splitext(file.filename)
    if file_ext.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại tệp không được hỗ trợ. Chỉ cho phép: {', '.join(allowed_extensions)}"
        )
        
    UPLOAD_DIR = "uploads"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
        
    attachment = upload_task_attachment_service(
        task_id=id,
        file_name=file.filename,
        file_path=file_path.replace("\\", "/"),
        file_size=file_size,
        mime_type=file.content_type,
        current_user=current_user,
        db=db
    )
    
    attachment_data = AttachmentResponse.model_validate(attachment)
    return create_response(
        request=req,
        status_code=status.HTTP_201_CREATED,
        message="Tải lên tệp đính kèm thành công!",
        data=attachment_data
    )


@router.get(
    "/{id}/attachments",
    status_code=status.HTTP_200_OK,
    summary="Lấy danh sách tệp đính kèm",
    description="Xem danh sách tất cả các tệp đính kèm đã tải lên của công việc này. Chỉ thành viên dự án mới được xem."
)
def get_attachments(
    id: int, # task_id
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    req: Request = None
):
    attachments = get_task_attachments_service(id, current_user, db)
    attachments_data = [AttachmentResponse.model_validate(a) for a in attachments]
    return create_response(
        request=req,
        status_code=status.HTTP_200_OK,
        message="Lấy danh sách tệp đính kèm thành công!",
        data=attachments_data
    )
