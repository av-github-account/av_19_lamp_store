from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models.order_model import Base
from app.db.session import engine
from app.api.v1.order_routes import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполняется при запуске сервиса
    Base.metadata.create_all(bind=engine)
    yield
    # Здесь можно добавить логику очистки при завершении (опционально)


app = FastAPI(lifespan=lifespan)

# Подключаем роуты
app.include_router(order_router, prefix="/orders", tags=["orders"])


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Order service root"}
