import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from common.protocol.order_protocol import OrderOutProtocol


def to_dict(obj: Any) -> Any:
    if is_dataclass(obj):
        return {k: to_dict(v) for k, v in asdict(obj).items()}
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

def order_response_to_json(order_response: OrderOutProtocol) -> str:
    order_response_dict = to_dict(order_response)
    return json.dumps(order_response_dict)
