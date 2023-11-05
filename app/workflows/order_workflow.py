from datetime import timedelta, datetime
from decimal import Decimal
from dataclasses import dataclass
from typing import cast, Callable

from app.common.result import Result
from common.protocol.order_protocol import OrderProtocol

from.helper import lookup_delivery_days_by_area

# possible states in workflow
# happy path
@dataclass(frozen=True)
class UnverifiedOrder:
    item_id: str
    quantity: int
    customer_address: str # TODO 住所のオブジェクト化

@dataclass(frozen=True)
class VerifiedOrder:
    item_id: str
    quantity: int
    customer_address: str

@dataclass(frozen=True)
class Invoice:
    item_id: str
    quantity: int
    total_price: Decimal

@dataclass(frozen=True)
class ShippedInvoice:
    item_id: str
    quantity: int
    total_price: Decimal
    arrival_date: datetime

# error path
@dataclass(frozen=True)
class InvalidAddress:
    message: str
    code: str = "InvalidAddress"

@dataclass(frozen=True)
class ItemNotFound:
    message: str
    code: str = "ItemNotFound"

@dataclass(frozen=True)
class NonDeliverableArea:
    message: str
    code: str = "NonDeliverableArea"

type OrderError = InvalidAddress | ItemNotFound | NonDeliverableArea


# worlflow
def process_order(
    address_checker: Callable[[str], bool],
    product_catalog: Callable[[str], Decimal],
) -> Callable[[OrderProtocol], Result[ShippedInvoice, OrderError]]:

    def _process_order_inner(
        order: OrderProtocol
    ) -> Result[ShippedInvoice, OrderError]:

        return (
            Result.Ok(cast(UnverifiedOrder, order))
            .bind(review_order(address_checker))
            .bind(calculate_price(product_catalog))
            .bind(determine_arrival_date_for_japan)
        )

    return _process_order_inner


# tasks
def review_order(
        check_address_existence: Callable[[str], bool]
    ) -> Callable[[UnverifiedOrder], Result[VerifiedOrder, InvalidAddress]]:

    def _with_specific_check_method(
            order: UnverifiedOrder
    ) -> Result[VerifiedOrder, InvalidAddress]:

        if not check_address_existence(order.customer_address):
            # TODO: 例えば複数のエラー種類を和型にしようとすると「互換性がありません」と言われる。解決方法を調べる。
            return Result.Err(
                InvalidAddress("The provided address is invalid.")
            )

        res = VerifiedOrder(**order.__dict__)
        return Result.Ok(res)

    return _with_specific_check_method


def calculate_price(
    product_catalog: Callable[[str], Decimal]
) -> Callable[[VerifiedOrder], Result[Invoice, ItemNotFound]]:

    def _with_specific_catalog(order: VerifiedOrder) -> Result[Invoice, ItemNotFound]:

        try:
            item_price = product_catalog(order.item_id)
        except KeyError:
            return Result.Err(
                ItemNotFound(f"The item_id {order.item_id} is not found in the product catalog.")
            )

        total_price = order.quantity * item_price

        return (
            Result.Ok(
                Invoice(
                    item_id=order.item_id,
                    quantity=order.quantity,
                    total_price=total_price,
                )
            )
        )

    return _with_specific_catalog


def determine_arrival_date(
        lookup_days: Callable[[str], int | None],
        invoice: Invoice
) -> Result[ShippedInvoice, NonDeliverableArea]:

    DELIVERY_DAYS = lookup_days(invoice.item_id)
    if DELIVERY_DAYS is None:
        return Result.Err(
            NonDeliverableArea("Customer address is in an undeliverable area.")
        )

    arrival_date = datetime.now() + timedelta(days=DELIVERY_DAYS)

    return Result.Ok(
        ShippedInvoice(
            **invoice.__dict__,
            arrival_date=arrival_date
        )
    )

from functools import partial
# エリア-日数の対応表については焼き付ける
determine_arrival_date_for_japan = partial(determine_arrival_date, lookup_delivery_days_by_area)
