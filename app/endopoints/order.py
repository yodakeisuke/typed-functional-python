from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from common.mock.order_mock import dummy_product_catalog, mock_address_checker
from common.util.result import Err, Ok
from workflows.order_workflow import process_order

router = APIRouter()

@dataclass(frozen=True)
class OrderRequest:
    item_id: str
    quantity: int
    address_prefecture: str
    address_detail: str

    @field_validator("item_id", mode='before')
    def validate_item_id(cls, value: str) -> str:
        if len(value) != 10:
            raise ValueError("item_idは10桁でなければなりません。")
        if not value[:3].isalpha():
            raise ValueError("item_idの最初の3文字はアルファベットでなければなりません。")
        return value

    @field_validator("quantity", mode='before')
    def quantity_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("数量は1以上でなければなりません。")
        return value


@dataclass(frozen=True)
class OrderResponse:
    bill_amount: Decimal
    arrival_date: datetime
    delivery_address: str


@router.post("", operation_id="create_order", response_model=OrderResponse)
async def create_order(
    order: Annotated[
        OrderRequest,
        Body(
            examples=[
                {
                    "item_id": "ABC1234567",
                    "quantity": 5,
                    "address_prefecture": "東京都",
                    "address_detail": "丸の内１丁目",
                }
            ],
        ),
    ]
) -> OrderResponse:

    match process_order(mock_address_checker, dummy_product_catalog)(order):
        case Ok(o):
            return(
                OrderResponse(
                    bill_amount=o.total_price,
                    arrival_date=o.arrival_date,
                    delivery_address=o.delivery_address.prefecture + o.delivery_address.detail,
                )
            )
        case Err(e):
        # このレイヤーではFW依存機能や例外をガンガン使用する
            raise HTTPException(status_code=400, detail=e.message)
        case _:
            print("default case")
            raise HTTPException(status_code=500, detail="unexpected error in http layer")
