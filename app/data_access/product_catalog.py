from decimal import Decimal


def product_catalog(item_id: str) -> Decimal:
    # 本当はDBをread
    if item_id == "ABC1234567":
        return Decimal("19.99")
    elif item_id == "XYZ7891234":
        return Decimal("29.99")
    elif item_id == "ABC0000000":
        return Decimal("40.00")
    elif item_id == "AAA1111111":
        return Decimal("39.80")
    else:
        return Decimal("9.99")
