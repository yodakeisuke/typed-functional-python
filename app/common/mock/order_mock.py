from decimal import Decimal


def mock_address_checker(address: str) -> bool:
    return "Tokyo" in address

def dummy_product_catalog(item_id: str) -> Decimal:
    if item_id == "ABC1234567":
        return Decimal("19.99")
    elif item_id == "XYZ789":
        return Decimal("29.99")
    else:
        return Decimal("9.99")
