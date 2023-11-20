from dataclasses import dataclass
from typing import Any, Callable, TypeVar

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')

@dataclass(frozen=True)
class Ok[T]:
    value: T

    def bind(self, op: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        return op(self.value)

@dataclass(frozen=True)
class Err[E]:
    error: E

    def bind(self, op: Callable[[Any], 'Result[U, E]']) -> 'Result[U, E]':
        return self

type Result[T, E] = Ok[T] | Err[E]

def From(value: T) -> Result[T, Any]:
    return Ok(value)
