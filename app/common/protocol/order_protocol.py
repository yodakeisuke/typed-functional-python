from datetime import datetime
from decimal import Decimal
from typing import Protocol, Any

from common.models.order import ConvenienceStore, CustomerAddress, DeliveryMethod
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class OrderInProtocol(Protocol):
    item_id: str
    quantity: int
    delivery_method: DeliveryMethod
    shipping_to: CustomerAddress | ConvenienceStore

@dataclass(frozen=True)
class OrderErrorProtocol(Protocol):
    code: Any # strではリテラルをsubtypeにできない
    message: str

@dataclass(frozen=True)
class OrderOutProtocol(Protocol):
    bill_amount: Decimal
    arrival_date: datetime
    shipping_to: CustomerAddress | ConvenienceStore
