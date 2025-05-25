from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from pathlib import Path
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Заглушка логина
@app.post("/api/v1/admin/login")
def login(credentials: dict):
    return {"token": "stub-token", "admin_id": 1}

# 1) Папка для хранения загруженных файлов
MEDIA_DIR = Path("/media")
MEDIA_DIR.mkdir(exist_ok=True)

# 2) Статика: раздача файлов по URL /media/имя_файла
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# Новый endpoint для загрузки изображений
@app.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix
    if ext.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
        raise HTTPException(400, "Неподдерживаемый формат файла")
    filename = f"{uuid4().hex}{ext}"
    dest = MEDIA_DIR / filename
    data = await file.read()  # читаем весь файл
    dest.write_bytes(data)    # сохраняем
    # возвращаем URL, который будут использовать клиенты
    return {"image_url": f"/media/{filename}"}

@app.get("/health")
def health():
    return {"status": "ok"}






# # from fastapi import FastAPI
# # from pydantic import BaseModel

# # app = FastAPI()

# # class LoginSchema(BaseModel):
# #     username: str
# #     password: str

# # @app.post("/api/v1/admin/login")
# # def login(data: LoginSchema):
# #     # простая заглушка для авторизации админу
# #     return {"token": "stub-token", "admin_id": 1}

# # @app.get("/health")
# # def health():
# #     return {"status": "ok"}



# # # from fastapi import FastAPI

# # # app = FastAPI()

# # # @app.post("/admin/login")
# # # def login():
# # #     return {"message": "Admin login works!"}







from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from uuid import uuid4
# from pathlib import Path

# app = FastAPI()

# # CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Заглушка логина
# @app.post("/api/v1/admin/login")
# def login(credentials: dict):
#     return {"token": "stub-token", "admin_id": 1}

# # Новый endpoint для загрузки изображений
# @app.post("/api/v1/admin/upload-image")
# async def upload_image(file: UploadFile = File(...)):
#     media_dir = Path("/media")
#     media_dir.mkdir(parents=True, exist_ok=True)
#     ext = Path(file.filename).suffix
#     filename = f"{uuid4().hex}{ext}"
#     file_path = media_dir / filename
#     with file_path.open("wb") as f:
#         f.write(await file.read())
#     return {"url": f"/media/{filename}"}

# @app.get("/health")
# def health():
#     return {"status": "ok"}






# # from fastapi import FastAPI
# # from pydantic import BaseModel

# # app = FastAPI()

# # class LoginSchema(BaseModel):
# #     username: str
# #     password: str

# # @app.post("/api/v1/admin/login")
# # def login(data: LoginSchema):
# #     # простая заглушка для авторизации админу
# #     return {"token": "stub-token", "admin_id": 1}

# # @app.get("/health")
# # def health():
# #     return {"status": "ok"}



# # # from fastapi import FastAPI

# # # app = FastAPI()

# # # @app.post("/admin/login")
# # # def login():
# # #     return {"message": "Admin login works!"}
