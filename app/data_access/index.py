from typing import Protocol
from decimal import Decimal

from data_access.convenience_store import lookup_delivery_days
from data_access.japan_post import existence_check_japanese_address
from data_access.product_catalog import product_catalog
from data_access.deliverly_days import lookup_delivery_days_by_area


class AddressCheckerProtocol(Protocol):
    def __call__(self, prefecture: str, detail: str) -> bool:
        ...
existence_check_japanese_address = existence_check_japanese_address


class CatalogCheckerProtocol(Protocol):
    def __call__(self, item_id: str) -> Decimal:
        ...
product_catalog = product_catalog


class ToHome(Protocol):
    def __call__(self, prefecture: str) -> int:
        ...
class ToCVS(Protocol):
    def __call__(self, company: str, code: str) -> int | None:
        ...

type DeliveryDaysEstimatorProtocol = tuple[ToHome, ToCVS]

lookup_delivery_days = lookup_delivery_days
lookup_delivery_days_pack = (
    lookup_delivery_days_by_area,
    lookup_delivery_days,
)
