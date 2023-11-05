from typing import Callable, TypeVar, Any

from dataclasses import dataclass


@dataclass(frozen=True)
class Ok[T]:
    value: T

U = TypeVar('U')

@dataclass(frozen=True)
class Err[E]:
    value: E


class Result[T, E]:
    def __init__(self, value: Ok[T] | Err[E]) -> None:
        self._container = value


    def bind(self, op: Callable[[T], 'Result[U,E]'])  -> 'Result[U, E]':
        if isinstance(self._container, Ok):
            return op(self._container.value)
        return Result(Err(self._container.value))

    @classmethod
    def Ok(cls: type['Result[T, Any]'], value: T):
        return cls(Ok(value))

    @classmethod
    def Err(cls: type['Result[Any, E]'], value: E):
        return cls(Err(value))

    def unwrap(self):
        return self._container
