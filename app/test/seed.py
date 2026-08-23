from datetime import datetime, timedelta
from app.database.database import SessionLocal, engine, Base
from app.core.security import hash_password
from app.models.users import UserModel, UserRole
from app.models.projects import ProjectModel, ProjectMemberModel, MemberRole
from app.models.tasks import TaskModel, TaskStatus, TaskPriority

def seed_data():
    db = SessionLocal()
    try:
        print("1. Tạo cấu trúc bảng nếu chưa tồn tại...")
        Base.metadata.create_all(bind=engine)

        print("2. Xóa dữ liệu cũ (theo thứ tự khóa ngoại)...")
        db.query(TaskModel).delete()
        db.query(ProjectMemberModel).delete()
        db.query(ProjectModel).delete()
        db.query(UserModel).delete()
        db.commit()

        print("3. Seed danh sách Users...")
        admin = UserModel(
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True
        )
        user1 = UserModel(
            email="user1@example.com",
            password_hash=hash_password("user123"),
            full_name="Nguyen Van A",
            role=UserRole.USER,
            is_active=True
        )
        user2 = UserModel(
            email="user2@example.com",
            password_hash=hash_password("user123"),
            full_name="Tran Thi B",
            role=UserRole.USER,
            is_active=True
        )

        db.add_all([admin, user1, user2])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        print("4. Seed danh sách Projects...")
        project_alpha = ProjectModel(
            name="Dự án Alpha",
            description="Hệ thống quản lý chuỗi cung ứng logistics",
            owner_id=user1.id
        )
        project_beta = ProjectModel(
            name="Dự án Beta",
            description="Ứng dụng di động theo dõi sức khỏe",
            owner_id=user2.id
        )
        db.add_all([project_alpha, project_beta])
        db.commit()
        db.refresh(project_alpha)
        db.refresh(project_beta)

        print("5. Seed Project Members...")
        # A tham gia dự án Beta của B
        member1 = ProjectMemberModel(
            project_id=project_beta.id,
            user_id=user1.id,
            role=MemberRole.MEMBER
        )
        # B tham gia dự án Alpha của A
        member2 = ProjectMemberModel(
            project_id=project_alpha.id,
            user_id=user2.id,
            role=MemberRole.MEMBER
        )
        db.add_all([member1, member2])
        db.commit()

        print("6. Seed danh sách Tasks...")
        task1 = TaskModel(
            project_id=project_alpha.id,
            title="Thiết lập Database schema",
            description="Thiết kế và cấu hình PostgreSQL",
            assignee_id=user1.id,
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=datetime.now() + timedelta(days=3)
        )
        task2 = TaskModel(
            project_id=project_alpha.id,
            title="Tạo API Authentication",
            description="Viết API Login, Register sử dụng JWT",
            assignee_id=user2.id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=datetime.now() + timedelta(days=5)
        )
        task3 = TaskModel(
            project_id=project_beta.id,
            title="Thiết kế UI/UX",
            description="Thiết kế giao diện bằng Figma",
            assignee_id=user2.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            due_date=datetime.now() + timedelta(days=7)
        )
        db.add_all([task1, task2, task3])
        db.commit()

        print(" Seed dữ liệu mẫu thành công!")

    except Exception as e:
        db.rollback()
        print(f"Có lỗi xảy ra trong quá trình seed: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()