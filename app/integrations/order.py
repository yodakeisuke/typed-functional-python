from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from data_access.index import product_catalog, existence_check_japanese_address, lookup_delivery_days_pack

from workflows.order_workflow import process_order

from common.models.order import ConvenienceStore, CustomerAddress, DeliveryMethod
from common.util.result import Err, Ok

from common.serializer.order import order_response_to_json
from common.client_api.pub_event import send_event


from docs.order_examle import home_delivery_example, convenience_store_delivery_example


# 外部通信(http、DB書き込み、他のサービスへのイベント通知/キューイングなど)レイヤ。
# 非純粋な領域。このレイヤーではFW依存機能や例外をガンガン使用する
# CONSIDER: エンドポイント(httpの捌き)の責務とサービスの責務レイヤーに分割しても良いかもしれない。

router = APIRouter()


@dataclass(frozen=True)
class OrderRequest:
    item_id: str
    quantity: int
    delivery_method: DeliveryMethod
    shipping_to: CustomerAddress | ConvenienceStore

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
    shipping_to: CustomerAddress | ConvenienceStore


@router.post("", operation_id="create_order", response_model=OrderResponse)
async def create_order(
    order: Annotated[
        OrderRequest,
        Body(
            openapi_examples={
                "home_delivery": home_delivery_example,
                "convenience_store_delivery": convenience_store_delivery_example,
            }
        ),
    ]
) -> OrderResponse:

    order_workflow = process_order(
        existence_check_japanese_address,
        product_catalog,
        lookup_delivery_days_pack,
    )

    match order_workflow(order):
        case Ok(o):
            ordered_event = OrderResponse(
                    bill_amount=o.bill_amount,
                    arrival_date=o.arrival_date,
                    shipping_to=o.shipping_to,
                )
            send_event(order_response_to_json(ordered_event))
            return ordered_event
        case Err(e):
            raise HTTPException(status_code=400, detail=e.message)
        case _:
            raise HTTPException(status_code=500, detail="unexpected error in http layer")
