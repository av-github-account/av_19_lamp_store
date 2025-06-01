# admin_service/app/main.py

from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from pathlib import Path
from uuid import uuid4
import os

from app.db.base import Base
from app.db.session import engine, get_db
from app.api.v1.admin_routes import router as admin_router
from app.core.security import get_current_admin  # Импорт из core.security как в admin_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    При старте создаём все таблицы (в том числе таблицу 'admins'),
    а затем проверяем, есть ли в базе хотя бы один администратор.
    Если нет — создаём дефолтного из переменных окружения.
    """
    Base.metadata.create_all(bind=engine)

    db: Session = next(get_db())
    try:
        from app.services.auth_service import get_admin_count, create_admin
        from app.schemas.admin_schema import AdminCreate

        if get_admin_count(db) == 0:
            username = os.getenv("ADMIN_DEFAULT_USERNAME")
            password = os.getenv("ADMIN_DEFAULT_PASSWORD")
            if username and password:
                create_admin(db, AdminCreate(username=username, password=password))
    finally:
        db.close()

    yield
    # Здесь можно добавить логику при завершении сервиса, если потребуется

app = FastAPI(lifespan=lifespan)

# Монтируем статические файлы из /media
app.mount("/media", StaticFiles(directory="/media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/", tags=["root"])
def root():
    return {"message": "Admin service root"}

@app.post(
    "/api/v1/admin/upload-image",
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить изображение"
)
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    """
    1) Проверяем, что текущий пользователь — админ (Depends(get_current_admin)).
    2) Генерируем уникальное имя файла (uuid4 + расширение).
    3) Сохраняем файл в /media.
    4) Возвращаем JSON с ключом "url": "/media/{имя_файла}".
    """
    media_dir = Path("/media")
    media_dir.mkdir(parents=True, exist_ok=True)

    original_filename = file.filename
    if not original_filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(original_filename).suffix
    new_filename = f"{uuid4().hex}{ext}"
    destination = media_dir / new_filename

    with destination.open("wb") as buffer:
        buffer.write(await file.read())

    return {"url": f"/media/{new_filename}"}
