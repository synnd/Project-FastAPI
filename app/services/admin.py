from sqlalchemy.orm import Session
from app.models.users import UserModel

def get_users_service(
    db: Session, 
    name: str = None, 
    email: str = None, 
    is_active: bool = None, 
    page: int = 1, 
    limit: int = 10
):
    
    query = db.query(UserModel)
    
    if name:
        query = query.filter(UserModel.full_name.ilike(f"%{name}%"))
        
    if email:
        query = query.filter(UserModel.email.ilike(f"%{email}%"))
        
    if is_active is not None:
        query = query.filter(UserModel.is_active == is_active)
        
    
    total = query.count()
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()
    
    return users, total