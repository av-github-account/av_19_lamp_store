from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.admin_model import Admin
from app.schemas.admin_schema import AdminCreate
from app.core.security import verify_password, get_password_hash

def get_admin_by_username(db: Session, username: str) -> Admin:
    return db.query(Admin).filter(Admin.username == username).first()

def authenticate_admin(db: Session, username: str, password: str) -> Admin | bool:
    admin = get_admin_by_username(db, username)
    if not admin:
        return False
    if not verify_password(password, admin.hashed_password):
        return False
    return admin

def create_admin(db: Session, admin_in: AdminCreate) -> Admin:
    existing = get_admin_by_username(db, admin_in.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    hashed = get_password_hash(admin_in.password)
    db_admin = Admin(username=admin_in.username, hashed_password=hashed)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def get_admin_count(db: Session) -> int:
    """
    Возвращает количество записей в таблице admins.
    """
    return db.query(Admin).count()