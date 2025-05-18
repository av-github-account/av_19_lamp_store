from sqlalchemy.orm import Session
from datetime import datetime

from app.models.order_model import Order, OrderItem, OrderStatusEnum
from app.schemas.order_schema import OrderCreate, OrderUpdate


# ===== 🔧 Генерация уникального order_name =====
def generate_order_name(db: Session) -> str:
    today_str = datetime.utcnow().strftime("%Y%m%d")
    last_order = (
        db.query(Order)
        .filter(Order.order_name.like(f"ORD-{today_str}-%"))
        .order_by(Order.id.desc())
        .first()
    )
    number = 1
    if last_order:
        try:
            last_number = int(last_order.order_name.split("-")[-1])
            number = last_number + 1
        except ValueError:
            pass  # fallback if order_name is malformed
    return f"ORD-{today_str}-{number:04d}"


# ===== Создание заказа =====
def create_order(db: Session, data: OrderCreate):
    # Генерация уникального номера заказа
    order_name = generate_order_name(db)

    # Расчёт итоговой суммы по заказу
    total_price = sum(item.quantity * item.unit_price for item in data.items)

    order = Order(
        order_name=order_name,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        total_price=total_price,
        comment=data.comment,
        status=OrderStatusEnum.NEW,  # установка начального статуса
    )

    db.add(order)
    db.flush()  # получить order.id до коммита

    # Добавление позиций заказа
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


# ===== Получить один заказ =====
def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()


# ===== Получить все заказы =====
def get_all_orders(db: Session):
    return db.query(Order).all()


# ===== Обновить заказ =====
def update_order(db: Session, order_id: int, data: OrderUpdate):
    order = get_order(db, order_id)
    if not order:
        return None

    for field, value in data.dict(exclude_unset=True).items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order


# ===== Отменить заказ (PATCH) =====
def cancel_order(db: Session, order_id: int):
    order = get_order(db, order_id)
    if not order:
        return None
    order.status = OrderStatusEnum.CANCELLED

    db.commit()
    return {"message": "Order cancelled"}
