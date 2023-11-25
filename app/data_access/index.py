from typing import NamedTuple, Callable, Optional

from data_access.convenience_store import lookup_delivery_days
from data_access.japan_post import existence_check_japanese_address
from data_access.product_catalog import product_catalog
from data_access.deliverly_days import lookup_delivery_days_by_area

product_catalog = product_catalog
lookup_delivery_days = lookup_delivery_days
existence_check_japanese_address = existence_check_japanese_address

lookup_delivery_days_pack = (
    lookup_delivery_days_by_area,
    lookup_delivery_days,
)
