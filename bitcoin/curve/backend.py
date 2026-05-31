"""Abstract interface for pluggable secp256k1 backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcoin.curve.point import Point


class CurveBackend(ABC):
    """Abstract secp256k1 backend with eight operations."""

    @abstractmethod
    def negate(self, point: Point) -> Point:
        ...

    @abstractmethod
    def add(self, left: Point, right: Point) -> Point:
        ...

    @abstractmethod
    def double(self, point: Point) -> Point:
        ...

    @abstractmethod
    def multiply(self, scalar: int, point: Point) -> Point:
        ...

    @abstractmethod
    def is_on_curve(self, point: Point) -> bool:
        ...

    @abstractmethod
    def sqrt(self, value: int) -> int:
        ...

    @abstractmethod
    def parse_sec(self, data: bytes) -> Point:
        ...

    @abstractmethod
    def serialize_sec(self, point: Point, compressed: bool = True) -> bytes:
        ...
