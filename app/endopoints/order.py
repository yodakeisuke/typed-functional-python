from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Body
from pydantic import validator
from pydantic.dataclasses import dataclass


router = APIRouter()

@dataclass(frozen=True)
class OrderRequest:
    item_id: str
    quantity: int
    customer_address: str

    @validator("item_id", pre=True, always=True)
    def validate_item_id(cls, value: str) -> str:
        if len(value) != 10:
            raise ValueError("item_idは10桁でなければなりません。")
        if not value[:3].isalpha():
            raise ValueError("item_idの最初の3文字はアルファベットでなければなりません。")
        return value

    @validator("quantity", pre=True, always=True)
    def quantity_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("数量は1以上でなければなりません。")
        return value


@dataclass(frozen=True)
class OrderResponse:
    item_name: str
    bill_amount: int
    arrival_date: datetime

@router.post("", operation_id="create_order", response_model=OrderResponse)
async def create_order(
    order: Annotated[
        OrderRequest,
        Body(
            examples=[
                {
                    "item_id": "ABC1234567",
                    "quantity": 2,
                    "customer_address": "123-456 Tokyo, Japan"
                }
            ],
        ),
    ]
) -> OrderResponse:

    return OrderResponse(
        item_name="Sample Item",
        bill_amount=order.quantity * 10,
        arrival_date=datetime.now() + timedelta(days=3),
    )
