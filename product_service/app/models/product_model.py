from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.base import Base  


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    image_url = Column(String)
    is_active = Column(Boolean, default=True)

