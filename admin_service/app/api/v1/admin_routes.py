from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.models.admin_model import Admin
from app.schemas.admin_schema import Token, AdminOut, AdminCreate
from app.services.auth_service import authenticate_admin, create_admin
from app.core.security import create_access_token, get_current_admin
from app.db.session import get_db

router = APIRouter()

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    admin = authenticate_admin(db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Имя пользователя или пароль неверны",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Добавляем ключ "is_admin": True в payload
    access_token = create_access_token(data={"sub": admin.username, "is_admin": True})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=AdminOut)
def register_admin(
    admin_in: AdminCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    POST /api/v1/admin/register
    Создаёт нового админа (только если текущий токен валиден).
    """
    admin = create_admin(db, admin_in)
    return admin

@router.get("/me", response_model=AdminOut)
def read_admin_me(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    GET /api/v1/admin/me
    Возвращает информацию о текущем (залогиненом) администраторе.
    """
    return current_admin
