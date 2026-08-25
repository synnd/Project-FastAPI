from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.database import Base

class ActivityLogModel(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Người thực hiện
    action = Column(String(255), nullable=False)                      # Tên hành động
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True) # Dự án liên quan
    details = Column(Text, nullable=True)                             # Mô tả chi tiết
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Các quan hệ liên kết
    user = relationship("UserModel")
    project = relationship("ProjectModel")