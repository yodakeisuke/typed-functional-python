from typing import NewType


DeliveryDaysRequired = NewType('DeliveryDaysRequired', int)

def lookup_delivery_days_by_area(area: str) -> DeliveryDaysRequired | None:
    match area:
        case "東京":
            return DeliveryDaysRequired(1)
        case "神奈川":
            return DeliveryDaysRequired(2)
        case "千葉":
            return DeliveryDaysRequired(3)
        case "埼玉":
            return DeliveryDaysRequired(5)
        case _:
            return None
