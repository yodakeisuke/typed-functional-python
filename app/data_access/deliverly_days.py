type DaysNeeded = int

def lookup_delivery_days_by_area(area: str) -> DaysNeeded | None:
    match area:
        case "東京都":
            return 1
        case "神奈川県":
            return 2
        case "千葉県":
            return 3
        case "埼玉県":
            return 5
        case _:
            return None
