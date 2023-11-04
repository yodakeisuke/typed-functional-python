from datetime import timedelta, datetime
from pydantic.dataclasses import dataclass


# states in workflow
@dataclass(frozen=True)
class UnverifiedOrder:
    item_id: str
    quantity: int
    customer_address: str

@dataclass(frozen=True)
class VerifiedOrder:
    item_id: str
    quantity: int
    customer_address: str

@dataclass(frozen=True)
class Invoice:
    item_id: str
    quantity: int
    total_price: int

@dataclass(frozen=True)
class ShippedInvoice:
    item_id: str
    quantity: int
    total_price: int
    arrival_date: datetime


# worlflow
def process_order(
    order: UnverifiedOrder
) -> ShippedInvoice:

    verified_order = review_order(order)
    invoice = calculate_price(verified_order)
    shipped_invoice = determine_arrival_date(invoice)

    return shipped_invoice


# tasks
def review_order(order: UnverifiedOrder) -> VerifiedOrder:
    # todo: implement review logic
    return VerifiedOrder(**order.__dict__)

def calculate_price(order: VerifiedOrder) -> Invoice:
    ITEM_PRICE = 10  # todo: implement price logic
    total_price = order.quantity * ITEM_PRICE
    return Invoice(
        item_id=order.item_id,
        quantity=order.quantity,
        total_price=total_price,
    )

def determine_arrival_date(invoice: Invoice) -> ShippedInvoice:
    DELIVERY_DAYS = 3  # todo: implement delivery logic
    arrival_date = datetime.now() + timedelta(days=DELIVERY_DAYS)
    return ShippedInvoice(
        **invoice.__dict__,
        arrival_date=arrival_date
    )
