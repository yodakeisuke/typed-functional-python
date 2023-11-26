from datetime import datetime
from decimal import Decimal
from typing import Protocol

from common.models.order import ConvenienceStore, CustomerAddress, DeliveryMethod
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class OrderProtocol(Protocol):
    item_id: str
    quantity: int
    delivery_method: DeliveryMethod
    shipping_to: CustomerAddress | ConvenienceStore

@dataclass(frozen=True)
class OrderErrorProtocol(Protocol):
    message: str
    code: str

@dataclass(frozen=True)
class OrderResProtocol(Protocol):
    bill_amount: Decimal
    arrival_date: datetime
    shipping_to: CustomerAddress | ConvenienceStore
