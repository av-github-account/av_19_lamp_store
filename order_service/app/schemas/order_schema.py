from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    NEW = "Новый"
    CANCELLED = "Отменен"
    IN_PROGRESS = "В работе"
    READY = "Готов к выдаче"
    WAITING_PAYMENT = "Ожидание оплаты"
    COMPLETED = "Выполнен"


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    # unit_price: float
    class Config:
        # Любые лишние поля (например, unit_price из JSON) будут проигнорированы
        extra = "ignore"

class OrderItemOut(OrderItemCreate):
    id: int

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    delivery_address: str
    comment: Optional[str] = None
    status: OrderStatusEnum = OrderStatusEnum.NEW
    items: List[OrderItemCreate]


class OrderOut(BaseModel):
    id: int
    order_name: str
    order_date: datetime
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    delivery_address: str
    total_price: float
    status: OrderStatusEnum
    comment: Optional[str]
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    delivery_address: Optional[str] = None
    comment: Optional[str] = None
    status: Optional[OrderStatusEnum] = None
    items: Optional[List[OrderItemCreate]] = None
