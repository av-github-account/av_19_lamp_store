from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.product_routes import router as product_router

app = FastAPI()

# Разрешаем запросы с фронтенда через API Gateway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутер товаров по пути, который проксирует Gateway
app.include_router(
    product_router,
    prefix="/api/v1/products",
    tags=["products"]
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# from fastapi import FastAPI
# from contextlib import asynccontextmanager

# from app.models.product_model import Base
# from app.db.session import engine
# from app.api.v1.product_routes import router as product_router


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # выполняется при запуске сервиса
#     Base.metadata.create_all(bind=engine)
#     yield
#     # здесь можно делать очистку, если нужно (on_shutdown)


# app = FastAPI(lifespan=lifespan)

# # Подключаем роуты
# app.include_router(product_router, prefix="/products", tags=["products"])


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# @app.get("/")
# def root():
#     return {"message": "Product service root"}
