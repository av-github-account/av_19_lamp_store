import os

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order_model import Order, OrderItem, OrderStatusEnum
from app.schemas.order_schema import OrderCreate, OrderUpdate  # ← сохранили OrderUpdate

# URL для доступа к product_service через gateway
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://gateway:8000")


def create_order(db: Session, data: OrderCreate) -> Order:
    # 1) Создаём объект заказа и сразу добавляем в сессию
    order = Order(
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        comment=data.comment,
        status=data.status
    )
    db.add(order)
    # ↓ Убрали преждевременный db.flush() — он пытался вставить заказ с total_price=None

    total_amount = 0.0

    for item_in in data.items:
        # 2) Тянем цену и остаток через gateway → product_service
        try:
            resp = httpx.get(
                f"{PRODUCT_SERVICE_URL}/api/v1/products/{item_in.product_id}",
                timeout=5.0
            )
            resp.raise_for_status()
            prod = resp.json()
        except httpx.HTTPStatusError:
            raise HTTPException(404, f"Product {item_in.product_id} not found")
        except Exception as e:
            raise HTTPException(502, f"Error contacting product service: {e}")

        price = prod["price"]
        stock = prod["stock_quantity"]

        if item_in.quantity > stock:
            raise HTTPException(
                400,
                f"Insufficient stock for product {item_in.product_id}: "
                f"available {stock}, requested {item_in.quantity}"
            )

        # 3) Добавляем позицию к заказу, связывая через relationship
        order_item = OrderItem(
            order=order,                 # SQLAlchemy сам проставит order_id
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            unit_price=price
        )
        db.add(order_item)

        total_amount += price * item_in.quantity

    # 4) Присваиваем total_price ДО коммита, чтобы не было NULL
    order.total_price = total_amount

    # 5) Коммитим заказ вместе с позициями
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order:
    return db.query(Order).filter(Order.id == order_id).first()


def get_all_orders(db: Session):
    return db.query(Order).all()


def update_order(db: Session, order_id: int, data: OrderUpdate) -> Order:
    order = db.query(Order).get(order_id)
    if not order:
        return None
    # Обновляем только изменённые поля заказа, не трогая позиции или цену
    for field, value in data.dict(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order_id: int):
    order = db.query(Order).get(order_id)
    if not order:
        return None
    order.status = OrderStatusEnum.CANCELLED
    db.commit()
    return {"message": "Order cancelled"}
