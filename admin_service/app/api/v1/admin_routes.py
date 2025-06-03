from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import os
from uuid import uuid4
import httpx

from app.models.admin_model import Admin
from app.schemas.admin_schema import Token, AdminOut, AdminCreate
from app.services.auth_service import authenticate_admin, create_admin
from app.core.security import create_access_token, get_current_admin
from app.db.session import get_db

# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session

# from app.models.admin_model import Admin
# from app.schemas.admin_schema import Token, AdminOut, AdminCreate
# from app.services.auth_service import authenticate_admin, create_admin
# from app.core.security import create_access_token, get_current_admin
# from app.db.session import get_db

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


@router.post("/upload-image", status_code=status.HTTP_200_OK)
async def upload_image(
    *,
    # Текущий админ, чтобы ручка была защищена JWT:
    current_admin = Depends(get_current_admin),
    # product_id передаём как form-поле
    product_id: int = Form(...),
    file: UploadFile = File(...),
):
    """
    1) Сохраняем файл в /media/products/<uuid>.<ext>
    2) Обновляем в product_service поле image_url для указанного product_id
    3) Возвращаем {"image_url": "..."}
    """
    # 1) Убедимся, что каталог /media/products существует
    media_dir = "/media/products"
    os.makedirs(media_dir, exist_ok=True)

    # 2) Составляем уникальное имя файла
    filename_ext = os.path.splitext(file.filename)[1]  # например, ".jpg" или ".png"
    unique_name = f"{uuid4().hex}{filename_ext}"
    save_path = os.path.join(media_dir, unique_name)

    # 3) Сохраняем файл в файловую систему контейнера
    content = await file.read()
    with open(save_path, "wb") as f_out:
        f_out.write(content)

    # 4) Формируем URL для отдачи (через gateway → proxy_media)
    new_image_url = f"/media/products/{unique_name}"

    # 5) Обновляем товар в product_service:
    #    — Сначала проверяем, что product с таким ID существует
    product_service_base = "http://product_service:8000/api/v1/products"
    async with httpx.AsyncClient() as client:
        # 5.1) GET /api/v1/products/{product_id}
        get_resp = await client.get(f"{product_service_base}/{product_id}")
        if get_resp.status_code == 404:
            # Вернём 404, если товар не найден
            raise HTTPException(status_code=404, detail="Product not found")
        get_resp.raise_for_status()
        prod_data = get_resp.json()

        # 5.2) Подготовим payload для обновления:
        # Обязательно включаем ВСЕ поля, которые требует ProductUpdate:
        #   { name, description, price, stock_quantity, image_url, is_active }
        update_payload = {
            "name": prod_data["name"],
            "description": prod_data["description"],
            "price": prod_data["price"],
            "stock_quantity": prod_data["stock_quantity"],
            "image_url": new_image_url,
            "is_active": prod_data["is_active"],
        }

        # 5.3) PUT /api/v1/products/{product_id} с новым image_url
        put_resp = await client.put(
            f"{product_service_base}/{product_id}",
            json=update_payload
        )
        put_resp.raise_for_status()

    # 6) Возвращаем клиенту новый URL картинки
    return {"image_url": new_image_url}