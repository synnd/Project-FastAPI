from fastapi import FastAPI, Depends
from app.database.database import Base, engine,get_db
from app.models.projects import ProjectMemberModel, ProjectModel
from app.models.users import UserModel
from app.models.tasks import TaskModel, CommentModel, AttachmentModel
from app.models.activity_log import ActivityLogModel
from app.schemas.response import register_exception_handlers

from app.router.auth import router as auth_router
from app.router.users import router as user_router
from app.router.admin import router as admin_router
from app.router.projects import router as project_router
from app.router.project_member import router as project_member_router
from app.router.tasks import router as task_router

Base.metadata.create_all(engine)

from app.dependencles.dependencles import get_current_admin
from app.models.users import UserModel
from sqlalchemy.orm import Session

app = FastAPI(
    title=" TEAM PROJECT MANAGEMENT API",
    description="Hệ thống quản lý Project",
    version="1.0.0"
)

register_exception_handlers(app)

@app.get('/', tags=["SYSTEM"])
def start_project(current_admin = Depends(get_current_admin),db : Session=Depends(get_db)):
    
    total_user = db.query(UserModel).count()
    return {
        "message": "Server đang hoạt động",
        "total_user" :total_user
    }

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(project_router)
app.include_router(project_member_router)
app.include_router(task_router)