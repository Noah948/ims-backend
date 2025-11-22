from sqlalchemy.orm import Session
from models.user_model import User, UserCreate

def create_user(db: Session, data: UserCreate):
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
