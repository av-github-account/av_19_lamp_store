from fastapi import HTTPException
from sqlalchemy.orm import Session

# Импортируем модели из конкретных модулей
from app.models.order_model import Order
from app.models.order_item_model import OrderItem
from app.models.product_model import Product

from app.schemas.order_schema import OrderCreate  # ваша Pydantic-схема

def create_order(db: Session, data: OrderCreate) -> Order:
    # 1) Создаём сам заказ (без позиций и цен)
    order = Order(
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address,
        comment=data.comment,
        status=data.status
    )
    db.add(order)
    db.flush()  # чтобы получить order.id, если нужно

    total_amount = 0.0

    for item_in in data.items:
        # 2) Берём актуальный объект товара и его цену из БД
        product = db.query(Product).filter(Product.id == item_in.product_id).first()
        if not product:
            raise HTTPException(404, f"Product {item_in.product_id} not found")

        # 3) Проверяем остатки
        if item_in.quantity > product.stock_quantity:
            raise HTTPException(
                400,
                f"Недостаточный остаток для товара {product.id}: "
                f"имеется {product.stock_quantity}, запрошено {item_in.quantity}"
            )

        # 4) Создаём позицию заказа с ценой из БД
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_in.quantity,
            unit_price=product.price  # цену берём только из product.price
        )
        db.add(order_item)

        # 5) Обновляем сумму и остаток на складе
        total_amount += product.price * item_in.quantity
        product.stock_quantity -= item_in.quantity

    # 6) Фиксируем общую сумму на заказе
    order.total_price = total_amount

    db.commit()
    db.refresh(order)
    return order




# from sqlalchemy.orm import Session
# from datetime import datetime

# from app.models.order_model import Order, OrderItem, OrderStatusEnum
# from app.schemas.order_schema import OrderCreate, OrderUpdate


# # ===== 🔧 Генерация уникального order_name =====
# def generate_order_name(db: Session) -> str:
#     today_str = datetime.utcnow().strftime("%Y%m%d")
#     last_order = (
#         db.query(Order)
#         .filter(Order.order_name.like(f"ORD-{today_str}-%"))
#         .order_by(Order.id.desc())
#         .first()
#     )
#     number = 1
#     if last_order:
#         try:
#             last_number = int(last_order.order_name.split("-")[-1])
#             number = last_number + 1
#         except ValueError:
#             pass  # fallback if order_name is malformed
#     return f"ORD-{today_str}-{number:04d}"


# # ===== Создание заказа =====
# def create_order(db: Session, data: OrderCreate):
#     # Генерация уникального номера заказа
#     order_name = generate_order_name(db)

#     # Расчёт итоговой суммы по заказу
#     total_price = sum(item.quantity * item.unit_price for item in data.items)

#     order = Order(
#         order_name=order_name,
#         customer_name=data.customer_name,
#         customer_email=data.customer_email,
#         customer_phone=data.customer_phone,
#         delivery_address=data.delivery_address,
#         total_price=total_price,
#         comment=data.comment,
#         status=OrderStatusEnum.NEW,  # установка начального статуса
#     )

#     db.add(order)
#     db.flush()  # получить order.id до коммита

#     # Добавление позиций заказа
#     for item in data.items:
#         db_item = OrderItem(
#             order_id=order.id,
#             product_id=item.product_id,
#             quantity=item.quantity,
#             unit_price=item.unit_price,
#         )
#         db.add(db_item)

#     db.commit()
#     db.refresh(order)
#     return order


# # ===== Получить один заказ =====
# def get_order(db: Session, order_id: int):
#     return db.query(Order).filter(Order.id == order_id).first()


# # ===== Получить все заказы =====
# def get_all_orders(db: Session):
#     return db.query(Order).all()


# # ===== Обновить заказ =====
# def update_order(db: Session, order_id: int, data: OrderUpdate):
#     order = get_order(db, order_id)
#     if not order:
#         return None

#     for field, value in data.dict(exclude_unset=True).items():
#         setattr(order, field, value)

#     db.commit()
#     db.refresh(order)
#     return order


# # ===== Отменить заказ (PATCH) =====
# def cancel_order(db: Session, order_id: int):
#     order = get_order(db, order_id)
#     if not order:
#         return None
#     order.status = OrderStatusEnum.CANCELLED

#     db.commit()
#     return {"message": "Order cancelled"}
