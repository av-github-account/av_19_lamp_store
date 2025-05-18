from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    order_name: str
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_address: str
    total_price: float
    comment: Optional[str] = ""
    items: List[OrderItemCreate]


class OrderItemOut(OrderItemCreate):
    id: int


class OrderOut(BaseModel):
    id: int
    order_name: str
    order_date: datetime
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_address: str
    total_price: float
    status: str
    comment: Optional[str]
    items: List[OrderItemOut]

    class Config:
        orm_mode = True


class OrderUpdate(BaseModel):
    status: Optional[str]
    delivery_address: Optional[str]
    comment: Optional[str]
