type DaysNeeded = int

def lookup_delivery_days(franchisor: str, code: str) -> DaysNeeded:
    match franchisor:
        case "SevenEleven":
            return 1
        case "FamilyMart":
            return 2
        case "Lawson":
            return 3
        case _:
            return 5
