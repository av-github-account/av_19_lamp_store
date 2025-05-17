from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.models.product_model import Base
from app.db.session import engine
from app.api.v1.product_routes import router as product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # выполняется при запуске сервиса
    Base.metadata.create_all(bind=engine)
    yield
    # здесь можно делать очистку, если нужно (on_shutdown)


app = FastAPI(lifespan=lifespan)

# Подключаем роуты
app.include_router(product_router, prefix="/products", tags=["products"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Product service root"}
