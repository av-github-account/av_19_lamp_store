from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.db.base import Base  

Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_name = Column(String, unique=True, nullable=False)
    order_date = Column(DateTime, default=datetime.utcnow)
    customer_name = Column(String)
    customer_email = Column(String)
    customer_phone = Column(String)
    delivery_address = Column(String)
    total_price = Column(Float)
    status = Column(String, default="новый")
    comment = Column(String)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer)
    quantity = Column(Integer)
    unit_price = Column(Float)

    order = relationship("Order", back_populates="items")
