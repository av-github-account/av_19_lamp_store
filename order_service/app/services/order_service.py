from sqlalchemy.orm import Session
from app.models.order_model import Order, OrderItem
from app.schemas.order_schema import OrderCreate, OrderUpdate


def create_order(db: Session, data: OrderCreate):
    order = Order(
        order_name=data.order_name,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        total_price=data.total_price,
        comment=data.comment,
    )
    db.add(order)
    db.flush()  # получить order.id до коммита

    for item in data.items:
        db_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        db.add(db_item)

    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


def get_all_orders(db: Session):
    return db.query(Order).all()


def update_order(db: Session, order_id: int, data: OrderUpdate):
    order = get_order(db, order_id)
    if not order:
        return None
    for field, value in data.dict(exclude_unset=True).items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


def cancel_order(db: Session, order_id: int):
    order = get_order(db, order_id)
    if not order:
        return None
    order.status = "отменен"
    db.commit()
    return {"message": "Order cancelled"}
