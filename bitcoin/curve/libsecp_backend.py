"""libsecp256k1-backed secp256k1 backend via the ``coincurve`` package."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from bitcoin.curve.backend import CurveBackend

if TYPE_CHECKING:
    from bitcoin.curve.point import Point

logger = logging.getLogger(__name__)


def check_libsecp256k1() -> None:
    """Raise ``ImportError`` if ``coincurve`` is not installed."""
    import coincurve  # noqa: F401


class LibsecpBackend(CurveBackend):
    """Backend using ``coincurve`` (libsecp256k1 C bindings).

    Falls back to the pure-Python implementation for operations the C
    library does not expose (negate, add, double).
    """

    def __init__(self) -> None:
        check_libsecp256k1()
        logger.debug(
            "LibsecpBackend initialised; negate/add/double fall back to "
            "pure Python because coincurve does not expose them."
        )

    def negate(self, point: Point) -> Point:
        from bitcoin.curve.operations import negate as _negate
        return _negate(point)

    def add(self, left: Point, right: Point) -> Point:
        from bitcoin.curve.operations import add as _add
        return _add(left, right)

    def double(self, point: Point) -> Point:
        from bitcoin.curve.operations import double as _double
        return _double(point)

    def multiply(self, scalar: int, point: Point) -> Point:
        import coincurve

        px = coincurve.PublicKey(point.to_sec_compressed())
        tweak = scalar.to_bytes(32, "big")
        new_pub = px.multiply(tweak)
        raw = new_pub.format()  # 33-byte compressed
        from bitcoin.encoding.sec import parse_sec
        return parse_sec(raw)

    def is_on_curve(self, point: Point) -> bool:
        import coincurve

        try:
            coincurve.PublicKey(point.to_sec_compressed())
            return True
        except ValueError:
            return False

    def sqrt(self, value: int) -> int:
        from bitcoin.curve.params import FIELD_PRIME
        from bitcoin.field.sqrt import sqrt as _sqrt
        return _sqrt(value, FIELD_PRIME)

    def parse_sec(self, data: bytes) -> Point:
        from bitcoin.encoding.sec import parse_sec
        return parse_sec(data)

    def serialize_sec(self, point: Point, compressed: bool = True) -> bytes:
        from bitcoin.encoding.sec import serialize_sec
        return serialize_sec(point, compressed)
