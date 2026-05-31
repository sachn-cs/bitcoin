"""Native pure-Python secp256k1 backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bitcoin.curve.backend import CurveBackend
from bitcoin.curve import operations as ops
from bitcoin.encoding.sec import parse_sec, serialize_sec
from bitcoin.field.sqrt import sqrt as field_sqrt

if TYPE_CHECKING:
    from bitcoin.curve.point import Point


class NativeBackend(CurveBackend):
    """Backend that delegates to the pure-Python ``operations`` module."""

    def negate(self, point: Point) -> Point:
        return ops.negate(point)

    def add(self, left: Point, right: Point) -> Point:
        return ops.add(left, right)

    def double(self, point: Point) -> Point:
        return ops.double(point)

    def multiply(self, scalar: int, point: Point) -> Point:
        return ops.multiply(scalar, point)

    def is_on_curve(self, point: Point) -> bool:
        return ops.is_on_curve(point)

    def sqrt(self, value: int) -> int:
        from bitcoin.curve.params import FIELD_PRIME
        return field_sqrt(value, FIELD_PRIME)

    def parse_sec(self, data: bytes) -> Point:
        return parse_sec(data)

    def serialize_sec(self, point: Point, compressed: bool = True) -> bytes:
        return serialize_sec(point, compressed)
