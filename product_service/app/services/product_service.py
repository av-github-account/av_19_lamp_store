from sqlalchemy.orm import Session
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate, ProductUpdate


# def get_all_products(db: Session):
#     return db.query(Product).filter(Product.is_active).all()
def get_all_products(db: Session):
    return db.query(Product).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, data: ProductCreate):
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate):
    product = get_product_by_id(db, product_id)
    if product:
        for field, value in data.dict().items():
            setattr(product, field, value)
        db.commit()
        db.refresh(product)
    return product


def deactivate_product(db: Session, product_id: int):
    product = get_product_by_id(db, product_id)
    if product:
        product.is_active = False
        db.commit()
        db.refresh(product)
    return (
        {"message": "Product deactivated"}
        if product
        else {"error": "Product not found"}
    )
