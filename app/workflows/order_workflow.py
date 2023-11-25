from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, cast

from common.models.order import ConvenienceStore, CustomerAddress, DeliveryMethod, Quantity
from common.protocol.order_protocol import OrderProtocol
from common.util.result import Err, From, Ok, Result


# states in workflow
# happy path
@dataclass(frozen=True)
class UnverifiedOrder:
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

@dataclass(frozen=True)
class ShippedInvoice:
    total_price: Decimal
    shipping_to: CustomerAddress | ConvenienceStore
    arrival_date: datetime

# error path
@dataclass(frozen=True)
class OrderError:
    code: str
    message: str

# data access requirement inerfaces
type ToHome = Callable[[str], int | None]
type ToCVS  = Callable[[str, str], int]
type LookUpDeliveryDaysMethods = tuple[ToHome, ToCVS]

# worlflow
def process_order(
    address_checker: Callable[[str, str], bool],
    product_catalog: Callable[[str], Decimal],
    lookup_delivery_days: LookUpDeliveryDaysMethods,
) -> Callable[[OrderProtocol], Result[ShippedInvoice, OrderError]]:

    def _process_order_inner(
        order: OrderProtocol
    ) -> Result[ShippedInvoice, OrderError]:

        return (
            From(cast(UnverifiedOrder, order))
            .bind(review_order(address_checker))
            .bind(calculate_price(product_catalog))
            .bind(determine_arrival_date(lookup_delivery_days))
        )

    return _process_order_inner


# tasks
def review_order(
        check_address_existence: Callable[[str, str], bool]
    ) -> Callable[[UnverifiedOrder], Result[VerifiedOrder, OrderError]]:

    def _with_specific_check_method(
            order: UnverifiedOrder
    ) -> Result[VerifiedOrder, OrderError]:

        match order.shipping_to:
            case CustomerAddress(prefecture=pref, detail=det):
                if not check_address_existence(pref, det):
                    return Err(
                        OrderError(code="InvalidAddress",message="The provided address is invalid.")
                    )
            case ConvenienceStore(company=_, store_code=code):
                if code == "":
                    return Err(
                        OrderError(code="InvalidStoreCode",message="The provided store code is invalid.")
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
                OrderError(code="Order", message=error)
            )
        )

    return _with_specific_check_method


def calculate_price(
    product_catalog: Callable[[str], Decimal]
) -> Callable[[VerifiedOrder], Result[Invoice, OrderError]]:

    def _with_specific_catalog(order: VerifiedOrder) -> Result[Invoice, OrderError]:

        try:
            item_price = product_catalog(order.item_id)
        except KeyError:
            return Err(
                OrderError(
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

    return _with_specific_catalog


def determine_arrival_date(
        lookup_days: LookUpDeliveryDaysMethods,
    )-> Callable[[Invoice], Result[ShippedInvoice, OrderError]]:

    def _determine_arrival_date_inner(
            invoice: Invoice
        ) -> Result[ShippedInvoice, OrderError]:

        match invoice.shipping_to:
            case CustomerAddress(prefecture=pref, detail=_):
                days = lookup_days[0](pref)
            case ConvenienceStore(company=comp, store_code=code):
                days = lookup_days[1](comp, code)

        if days is None:
            return Err(
                OrderError(
                    code="NonDeliverableArea",
                    message="Customer address is in an undeliverable area.",
                )
            )

        arrival_date = datetime.now() + timedelta(days=days)

        return Ok(
            ShippedInvoice(
                total_price=invoice.total_price,
                arrival_date=arrival_date,
                shipping_to=invoice.shipping_to
            )
        )

    return _determine_arrival_date_inner
