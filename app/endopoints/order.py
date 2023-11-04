from datetime import datetime, timedelta
from typing import Annotated, cast

from fastapi import APIRouter, Body
from pydantic import validator
from pydantic.dataclasses import dataclass

from app.workflows.order_workflow import UnverifiedOrder, ShippedInvoice, process_order

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
    item_id: str
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

    res = process_order(cast(UnverifiedOrder, order))

    return OrderResponse(
        item_id=res.item_id,
        bill_amount=res.total_price,
        arrival_date=res.arrival_date,
    )
