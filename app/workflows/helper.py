from typing import NewType

DeliveryDaysRequired = NewType('DeliveryDaysRequired', int)

def lookup_delivery_days_by_area(area: str) -> DeliveryDaysRequired | None:
    match area:
        case "東京都":
            return DeliveryDaysRequired(1)
        case "神奈川県":
            return DeliveryDaysRequired(2)
        case "千葉県":
            return DeliveryDaysRequired(3)
        case "埼玉県":
            return DeliveryDaysRequired(5)
        case _:
            return None
