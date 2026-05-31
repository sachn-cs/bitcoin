"""Secp256k1 curve arithmetic, backends, and the ``Point`` type.

Everything in this package is independent of Bitcoin transactions,
scripts, and signatures.
"""

from bitcoin.curve.params import (
    CURVE_A,
    CURVE_B,
    CURVE_ORDER,
    FIELD_PRIME,
    GENERATOR_X,
    GENERATOR_Y,
)
from bitcoin.curve.point import Point
from bitcoin.curve.backend import CurveBackend
from bitcoin.curve.native_backend import NativeBackend
from bitcoin.curve.libsecp_backend import LibsecpBackend, check_libsecp256k1
from bitcoin.curve.dispatch import (
    add,
    double,
    get_backend,
    is_on_curve,
    multiply,
    negate,
    normalize,
    normalize_non_negative,
    parse_public_key,
    serialize_public_key,
    set_backend,
    sqrt_field,
)

# Singleton points
GENERATOR = Point(x=GENERATOR_X, y=GENERATOR_Y)
INFINITY = Point(infinity=True)

__all__ = [
    "CURVE_A",
    "CURVE_B",
    "CURVE_ORDER",
    "CurveBackend",
    "FIELD_PRIME",
    "GENERATOR",
    "GENERATOR_X",
    "GENERATOR_Y",
    "INFINITY",
    "LibsecpBackend",
    "NativeBackend",
    "Point",
    "add",
    "check_libsecp256k1",
    "double",
    "get_backend",
    "is_on_curve",
    "multiply",
    "negate",
    "normalize",
    "normalize_non_negative",
    "parse_public_key",
    "serialize_public_key",
    "set_backend",
    "sqrt_field",
]
