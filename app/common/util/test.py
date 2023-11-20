import sys
sys.path.append('/Users/yk/work/fastAPI/typed_functional_python/app')

from common.util.result import Err, From, Ok, Result
from dataclasses import dataclass

@dataclass(frozen=True)
class Order:
    quantity: int

@dataclass(frozen=True)
class OrderError:
    code: str
    message: str

# 純粋関数のパイプラインの作成
def add_one(x: int) -> Result[Order, OrderError]:
    if x < 0:
        return Err(
            OrderError(
                code="InvalidArgument",
                message="x must be positive 1"
            )
        )
    return Ok(
        Order(x + 1)
    )

def multiply_by_two(o: Order) -> Result[Order, OrderError]:
    if o.quantity < 0:
        return Err(
            OrderError(
                code="InvalidArgument",
                message="x must be positive 2"
            )
        )
    return Ok(
        Order(o.quantity * 2)
    )

def run_pipeline(value: int) -> Result[Order, OrderError]:
    return From(value).bind(add_one).bind(multiply_by_two)



# パターンマッチで結果の取り出し
def printOrder(r: Result[Order, OrderError]):
    match r:
        case Ok(value):
            print(f"Ok: {value.quantity}")
        case Err(error):
            print(f"Error: {error}")
        case _:
            print("Unknown result type")

# パイプラインの実行と結果の取り出し
result = run_pipeline(3)
printOrder(result)
result = run_pipeline(-22)
printOrder(result)
