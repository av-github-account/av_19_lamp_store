from sqlalchemy import String, Integer, Float, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime
import enum
import uuid
from typing import List


class OrderStatusEnum(str, enum.Enum):
    NEW = "Новый"
    CANCELLED = "Отменен"
    IN_PROGRESS = "В работе"
    READY = "Готов к выдаче"
    WAITING_PAYMENT = "Ожидание оплаты"
    COMPLETED = "Выполнен"


def generate_order_name() -> str:
    now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"ORDER-{now}-{uuid.uuid4().hex[:6].upper()}"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_name: Mapped[str] = mapped_column(
        String, unique=True, default=generate_order_name, nullable=False
    )
    order_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    customer_name: Mapped[str] = mapped_column(String)
    customer_email: Mapped[str] = mapped_column(String)
    customer_phone: Mapped[str] = mapped_column(String)
    delivery_address: Mapped[str] = mapped_column(String)
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[OrderStatusEnum] = mapped_column(
        SqlEnum(
            OrderStatusEnum,
            native_enum=False,
            values_callable=lambda enum: [e.name for e in enum],
        ),
        default=OrderStatusEnum.NEW,
    )

    comment: Mapped[str] = mapped_column(String)

    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship(back_populates="items")
