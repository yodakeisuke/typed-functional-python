home_delivery_example = {
    "summary": "Home Delivery",
    "description": "An example of an order with home delivery.",
    "value": {
        "item_id": "ABC1234567",
        "quantity": 10,
        "delivery_method": "home",
        "shipping_to": {
            "prefecture": "東京都",
            "detail": "丸の内1-2-3なんちゃらビル"
        }
    }
}

convenience_store_delivery_example = {
    "summary": "Convenience Store Delivery",
    "description": "An example of an order with convenience store delivery.",
    "value": {
        "item_id": "XYZ7891234",
        "quantity": 6,
        "delivery_method": "convenience_store",
        "shipping_to": {
            "company": "SevenEleven",
            "store_code": "ABC123"
        }
    }
}
