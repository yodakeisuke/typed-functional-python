from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable, cast

from common.models.order import DeliveryAddress, Quantity
from common.protocol.order_protocol import OrderProtocol
from common.util.result import Err, From, Ok, Result

from .helper import lookup_delivery_days_by_area


# possible states in workflow
# happy path
@dataclass(frozen=True)
class UnverifiedOrder:
    item_id: str
    quantity: int
    address_prefecture: str
    address_detail: str

@dataclass(frozen=True)
class VerifiedOrder:
    item_id: str
    quantity: Quantity
    delivery_address: DeliveryAddress

@dataclass(frozen=True)
class Invoice:
    item_id: str
    quantity: Quantity
    total_price: Decimal
    delivery_address: DeliveryAddress

@dataclass(frozen=True)
class ShippedInvoice:
    total_price: Decimal
    delivery_address: DeliveryAddress
    arrival_date: datetime

# error path
@dataclass(frozen=True)
class OrderError:
    code: str
    message: str

# type OrderError = InvalidAddress | ItemNotFound | NonDeliverableArea
# CONSIDER: 本当は上記のようにしたいが出来なかった...Resultの型変数でUnionを受け入れられるように出来なかった。

# @dataclass(frozen=True)
# class InvalidAddress:
    # message: str
    # code: str = "InvalidAddress"

# @dataclass(frozen=True)
# class ItemNotFound:
    # message: str
    # code: str = "ItemNotFound"

# @dataclass(frozen=True)
# class NonDeliverableArea:
    # message: str
    # code: str = "NonDeliverableArea"

# worlflow
def process_order(
    address_checker: Callable[[str, str], bool],
    product_catalog: Callable[[str], Decimal],
) -> Callable[[OrderProtocol], Result[ShippedInvoice, OrderError]]:

    def _process_order_inner(
        order: OrderProtocol
    ) -> Result[ShippedInvoice, OrderError]:

        return (
            From(cast(UnverifiedOrder, order))
            .bind(review_order(address_checker))
            .bind(calculate_price(product_catalog))
            .bind(determine_arrival_date_for_japan)
        )

    return _process_order_inner


# tasks
def review_order(
        check_address_existence: Callable[[str, str], bool]
    ) -> Callable[[UnverifiedOrder], Result[VerifiedOrder, OrderError]]:

    def _with_specific_check_method(
            order: UnverifiedOrder
    ) -> Result[VerifiedOrder, OrderError]:

        if not check_address_existence(order.address_prefecture, order.address_detail):
            return Err(
                OrderError(code="InvalidAddress",message="The provided address is invalid.")
            )
        match Quantity.From(order.quantity):
            case Ok(value):
                return Ok(
                    VerifiedOrder(
                        item_id=order.item_id,
                        quantity=value,
                        delivery_address=DeliveryAddress(
                            prefecture=order.address_prefecture,
                            detail=order.address_detail,
                        )
                    )
                )
            case Err(error):
                return Err(
                    OrderError(code="Order", message=error)
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
                delivery_address=order.delivery_address,
                # CONSIDER: 明示的にintにキャストしないと型チェッカーがエラーを出してしまう...
                total_price=int(order.quantity) * item_price,
            )
        )

    return _with_specific_catalog


def determine_arrival_date(
        lookup_days: Callable[[str], int | None],
        invoice: Invoice
) -> Result[ShippedInvoice, OrderError]:

    days= lookup_days(invoice.delivery_address.prefecture)
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
            delivery_address=invoice.delivery_address
        )
    )


from functools import partial
# NOTE: エリア-日数の対応表については焼き付ける
determine_arrival_date_for_japan = partial(determine_arrival_date, lookup_delivery_days_by_area)
