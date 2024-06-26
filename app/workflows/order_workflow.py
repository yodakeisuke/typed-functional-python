from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, Literal

from common.protocol.order_protocol import OrderInProtocol, OrderOutProtocol, OrderErrorProtocol
from common.util.result import Err, From, Ok, Result
from common.models.order import ConvenienceStore, CustomerAddress, DeliveryMethod, Quantity
from data_access.index import  AddressCheckerProtocol,  CatalogCheckerProtocol, DeliveryDaysEstimatorProtocol


""" resulting events """
# happy path
@dataclass(frozen=True)
class ShippedInvoice(OrderOutProtocol):
    bill_amount: Decimal
    shipping_to: CustomerAddress | ConvenienceStore
    arrival_date: datetime

# error path
@dataclass(frozen=True)
class InvalidOrder(OrderErrorProtocol):
    code: Literal["InvalidAddress", "InvalidStoreCode", "InvalidQuantity"]
    message: str

@dataclass(frozen=True)
class OutOfStock(OrderErrorProtocol):
    code: Literal ["ItemNotFound"]
    message: str

@dataclass(frozen=True)
class Undeliverable(OrderErrorProtocol):
    code: Literal ["NonDeliverableArea"]
    message: str

type OrderError = InvalidOrder | OutOfStock | Undeliverable

""" state transition in workflow """
@dataclass(frozen=True)
class UnverifiedOrder(OrderInProtocol):
    item_id: str
    quantity: int
    delivery_method: DeliveryMethod
    shipping_to: CustomerAddress | ConvenienceStore

@dataclass(frozen=True)
class VerifiedOrder:
    item_id: str
    quantity: Quantity
    shipping_to: CustomerAddress | ConvenienceStore

@dataclass(frozen=True)
class Invoice:
    item_id: str
    quantity: Quantity
    total_price: Decimal
    shipping_to: CustomerAddress | ConvenienceStore


""" workflow entry point """
type ProcessOrderResult = Result[ShippedInvoice, OrderError]
def process_order(
        address_checker: AddressCheckerProtocol,
        product_catalog: CatalogCheckerProtocol,
        estimate_delivery_days: DeliveryDaysEstimatorProtocol,
    ) -> Callable[[OrderInProtocol], ProcessOrderResult]:

    def _process_order_core(
        order: OrderInProtocol
    ) -> ProcessOrderResult:

        return (
            From(order)
            .bind(review_order(address_checker))
            .bind(calculate_price(product_catalog))
            .bind(determine_arrival_date(estimate_delivery_days))
        )

    return _process_order_core

""" tasks """
type ReviewResult =Result[VerifiedOrder, InvalidOrder]
def review_order(
        check_address_existence: AddressCheckerProtocol
    ) -> Callable[[OrderInProtocol], ReviewResult]:

    def _review_order_core(order: OrderInProtocol) -> ReviewResult:
        match order.shipping_to:
            case CustomerAddress(prefecture=pref, detail=det):
                if not check_address_existence(pref, det):
                    return Err(
                        InvalidOrder(code="InvalidAddress",message="The provided address is invalid.")
                    )
            case ConvenienceStore(company=_, store_code=code):
                if code == "":
                    return Err(
                        InvalidOrder(code="InvalidStoreCode",message="The provided store code is invalid.")
                    )

        return Quantity.From(order.quantity).bind(
            lambda quantity: Ok(
                VerifiedOrder(
                    item_id=order.item_id,
                    quantity=quantity,
                    shipping_to=order.shipping_to
                )
            )
        ).or_else(
            lambda error: Err(
                InvalidOrder(code="InvalidQuantity", message=error)
            )
        )

    return _review_order_core


type CalcPriceResult = Result[Invoice, OutOfStock]
def calculate_price(
    product_catalog: CatalogCheckerProtocol
) -> Callable[[VerifiedOrder], CalcPriceResult]:

    def _calculate_price_core(order: VerifiedOrder) -> CalcPriceResult:
        try:
            item_price = product_catalog(order.item_id)
        except KeyError:
            return Err(
                OutOfStock(
                    code="ItemNotFound",
                    message=f"The item_id {order.item_id} is not found in the product catalog.")
            )
        return Ok(
            Invoice(
                item_id=order.item_id,
                quantity=order.quantity,
                shipping_to=order.shipping_to,
                # CONSIDER: 明示的にintにキャストしないと型チェッカーがエラーを出してしまう...
                total_price=int(order.quantity) * item_price,
            )
        )

    return _calculate_price_core

type ArrivalDateResult = Result[ShippedInvoice, Undeliverable]
def determine_arrival_date(
        lookup_days: DeliveryDaysEstimatorProtocol,
    )-> Callable[[Invoice], ArrivalDateResult]:

    def _determine_arrival_date_core(invoice: Invoice) -> ArrivalDateResult:
        match invoice.shipping_to:
            case CustomerAddress(prefecture=pref, detail=_):
                days = lookup_days[0](pref)
            case ConvenienceStore(company=comp, store_code=code):
                days = lookup_days[1](comp, code)

        if days is None:
            return Err(
                Undeliverable(
                    code="NonDeliverableArea",
                    message="Customer address is in an undeliverable area.",
                )
            )

        arrival_date = datetime.now() + timedelta(days=days)

        return Ok(
            ShippedInvoice(
                bill_amount=invoice.total_price,
                arrival_date=arrival_date,
                shipping_to=invoice.shipping_to
            )
        )

    return _determine_arrival_date_core
