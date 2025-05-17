from fastapi import FastAPI
from app.api.v1.product_routes import router as product_router

app = FastAPI()
app.include_router(product_router, prefix="/products", tags=["products"])

@app.get("/")
def root():
    return {"message": "Product service root"}
