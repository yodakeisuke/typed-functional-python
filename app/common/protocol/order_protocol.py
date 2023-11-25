from typing import Protocol
from pydantic.dataclasses import dataclass

from common.models.order import ConvenienceStore, CustomerAddress, DeliveryMethod



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
