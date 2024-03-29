from dataclasses import dataclass
from typing import Literal

from common.util.result import Err, Ok, Result


type DeliveryMethod = Literal["home", "convenience_store"]
type Franchisors = Literal["SevenEleven", "FamilyMart", "Lawson"]

@dataclass(frozen=True)
class CustomerAddress:
    prefecture: str
    detail: str


@dataclass(frozen=True)
class ConvenienceStore:
    company: Franchisors
    store_code: str


# Value Object Example
@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self):
        if not 1 <= self.value <= 99:
            raise ValueError("Quantity must be between 1 and 99")

    @staticmethod
    def From(value: int) -> Result['Quantity', str]:
        try:
            return Ok(Quantity(value))
        except ValueError as e:
            return Err(str(e))

    def __int__(self):
        return self.value

# CONSIDER: pydanticは、annotated-typesの内容を拾える？でもエラーは例外を返しそう。
# https://docs.pydantic.dev/latest/concepts/types/
