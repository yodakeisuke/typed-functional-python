from typing import Protocol

from pydantic.dataclasses import dataclass

@dataclass(frozen=True)
class OrderProtocol(Protocol):
    item_id: str
    quantity: int
    address_prefecture: str
    address_detail: str

@dataclass(frozen=True)
class OrderErrorProtocol(Protocol):
    message: str
    code: str
