from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int
    image_url: str


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    is_active: bool


class ProductOut(ProductBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
