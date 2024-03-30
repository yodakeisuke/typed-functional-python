from dataclasses import dataclass
from typing import Any, Callable, TypeVar

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')

@dataclass(frozen=True)
class Ok[T]:
    value: T

    def bind(self, op: Callable[[T], 'Result[U, Any]']) -> 'Result[U, Any]':
        return op(self.value)

    def or_else(self, op: Callable[[Any], 'Result[T, E]']) -> 'Result[T, E]':
        return self

@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind(self, op: Callable[[Any], 'Result[Any, E]']) -> 'Result[Any, E]':
        return self

    def or_else[F](self, op: Callable[[Any], 'Err[F]']) -> 'Err[F]':
        return op(self.error)

type Result[T, E] = Ok[T] | Err[E]

def From(value: T) -> Result[T, Any]:
    return Ok(value)
