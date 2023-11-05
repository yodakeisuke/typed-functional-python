from typing import Protocol
from datetime import datetime

from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class OrderProtocol(Protocol):
    item_id: str
    quantity: int
    customer_address: str

@dataclass(frozen=True)
class OrderErrorProtocol(Protocol):
    message: str
    code: str
