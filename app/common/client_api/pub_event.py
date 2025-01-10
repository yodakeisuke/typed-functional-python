def send_event(serialized_json: str, order_id: str, delivery_date: str) -> None:
    print(f"Sending event to external service: {serialized_json}")
    print(f"Order {order_id} status updated to 'shipped'")
    print(f"Delivery date: {delivery_date}")
