from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.order_schema import OrderCreate, OrderOut, OrderUpdate
from app.services.order_service import (
    create_order,
    get_order,
    get_all_orders,
    update_order,
)
from app.db.session import get_db

router = APIRouter()


@router.post("/", response_model=OrderOut)
def create(data: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, data)


@router.get("/", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return get_all_orders(db)


@router.get("/{order_id}", response_model=OrderOut)
def retrieve(order_id: int, db: Session = Depends(get_db)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.put("/{order_id}", response_model=OrderOut)
def update(order_id: int, data: OrderUpdate, db: Session = Depends(get_db)):
    order = update_order(db, order_id, data)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# @router.patch("/{order_id}")
# def cancel(order_id: int, db: Session = Depends(get_db)):
#     result = cancel_order(db, order_id)
#     if not result:
#         raise HTTPException(status_code=404, detail="Order not found")
#     return result
