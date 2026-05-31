"""Backend selection and dispatch for curve operations."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from bitcoin.curve.backend import CurveBackend
from bitcoin.curve.native_backend import NativeBackend

if TYPE_CHECKING:
    from bitcoin.curve.point import Point

logger = logging.getLogger(__name__)

_backend: CurveBackend | None = None


def get_backend() -> CurveBackend | None:
    """Return the current backend, or ``None`` to use the native default."""
    return _backend


def set_backend(backend: CurveBackend) -> None:
    """Set the active curve backend.

    Raises:
        TypeError: If *backend* is not a ``CurveBackend`` instance.
    """
    if not isinstance(backend, CurveBackend):
        raise TypeError(
            f"Expected CurveBackend instance, got {type(backend).__name__}."
        )
    global _backend
    _backend = backend


def _resolve_backend() -> CurveBackend:
    """Return the active backend or the default native backend."""
    if _backend is not None:
        return _backend
    return NativeBackend()


# ── Public dispatch functions ──────────────────────────────────────────


def negate(point: Point) -> Point:
    return _resolve_backend().negate(point)


def add(left: Point, right: Point) -> Point:
    return _resolve_backend().add(left, right)


def double(point: Point) -> Point:
    return _resolve_backend().double(point)


def multiply(scalar: int, point: Point) -> Point:
    return _resolve_backend().multiply(scalar, point)


def is_on_curve(point: Point) -> bool:
    return _resolve_backend().is_on_curve(point)


def sqrt_field(value: int) -> int:
    from bitcoin.curve.params import FIELD_PRIME
    return _resolve_backend().sqrt(value)


def parse_public_key(data: bytes) -> Point:
    return _resolve_backend().parse_sec(data)


def serialize_public_key(point: Point, compressed: bool = True) -> bytes:
    return _resolve_backend().serialize_sec(point, compressed)


def normalize(value: int) -> int:
    """Return *value* reduced to the range ``[0, FIELD_PRIME)``."""
    from bitcoin.curve.params import FIELD_PRIME
    return value % FIELD_PRIME


def normalize_non_negative(value: int, label: str = "value") -> int:
    """Thin wrapper over ``field.modular.validate_non_negative``."""
    from bitcoin.field import validate_non_negative
    return validate_non_negative(value, label)
