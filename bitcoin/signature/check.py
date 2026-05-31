"""Signature verification (ECDSAsig check)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bitcoin.curve import GENERATOR
from bitcoin.curve.dispatch import add, multiply, is_on_curve
from bitcoin.curve.params import CURVE_ORDER, FIELD_PRIME
from bitcoin.encoding.der import decode_der

if TYPE_CHECKING:
    from bitcoin.curve.point import Point


def recover_public_key(message: bytes, sig: bytes, flag: int) -> Point:
    """Recover the public key from a signature.

    Arguments:
        message: The 32-byte message hash.
        sig: The DER-encoded signature.
        flag: The recovery ID (``27..34``, ``35..42``, etc. for SegWit).

    Raises:
        ValueError: If recovery fails.
    """
    r, s = decode_der(sig)
    rec_id = (flag - 27) & 0x03
    compressed = bool((flag - 27) & 0x04)

    # Recover R point
    r_x = r
    r_y_sq = (pow(r_x, 3, FIELD_PRIME) + 7) % FIELD_PRIME
    r_y = pow(r_y_sq, (FIELD_PRIME + 1) // 4, FIELD_PRIME)
    if (r_y & 1) != (rec_id & 1):
        r_y = FIELD_PRIME - r_y

    from bitcoin.curve.point import Point
    r_point = Point(x=r_x, y=r_y)

    if not is_on_curve(r_point):
        raise ValueError("Recovered R point is not on the curve.")

    # e = -message mod n
    e = int.from_bytes(message, "big")
    e_inv = CURVE_ORDER - (e % CURVE_ORDER) if e % CURVE_ORDER != 0 else 0

    # s_inv = s^-1 mod n
    from bitcoin.field import inverse
    s_inv = inverse(s, CURVE_ORDER)

    r1 = multiply(s_inv, r_point)
    r2 = multiply((s_inv * e_inv) % CURVE_ORDER, GENERATOR)
    pub = add(r1, r2)

    if pub.infinity:
        raise ValueError("Recovered point is infinity.")

    if compressed:
        from bitcoin.encoding.sec import serialize_sec
        _ = serialize_sec(pub, compressed=True)

    return pub


def verify_sig(message: bytes, sig: bytes, public_key: Point) -> bool:
    """Verify an ECDSA signature against a public key.

    Arguments:
        message: The 32-byte message hash.
        sig: The DER-encoded signature.
        public_key: The public key ``Point``.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    try:
        r, s = decode_der(sig)
    except ValueError:
        return False

    if r < 1 or r >= CURVE_ORDER or s < 1 or s >= CURVE_ORDER:
        return False

    if not is_on_curve(public_key) or public_key.infinity:
        return False

    e = int.from_bytes(message, "big") % CURVE_ORDER
    if e == 0:
        return False

    from bitcoin.field import inverse
    s_inv = inverse(s, CURVE_ORDER)
    u1 = (e * s_inv) % CURVE_ORDER
    u2 = (r * s_inv) % CURVE_ORDER

    u1_g = multiply(u1, GENERATOR)
    u2_p = multiply(u2, public_key)
    point = add(u1_g, u2_p)

    if point.infinity:
        return False

    return (point.x % CURVE_ORDER) == r
