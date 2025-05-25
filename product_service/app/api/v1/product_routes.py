from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductOut
from app.services.product_service import (
    get_all_products,
    get_product_by_id,
    create_product,
    update_product,
    deactivate_product,
)
from app.db.session import get_db

router = APIRouter()


@router.get("/", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return get_all_products(db)


@router.get("/{product_id}", response_model=ProductOut)
def retrieve_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut)
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db, product)


@router.put("/{product_id}", response_model=ProductOut)
def modify_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    return update_product(db, product_id, data)


@router.patch("/{product_id}")
def disable_product(product_id: int, db: Session = Depends(get_db)):
    return deactivate_product(db, product_id)
