"""Pure-Python secp256k1 point arithmetic."""

from __future__ import annotations

from bitcoin.curve.params import CURVE_A, CURVE_B, FIELD_PRIME, CURVE_ORDER
from bitcoin.curve.point import Point
from bitcoin.field import inverse, sqrt


def negate(point: Point) -> Point:
    """Return the additive inverse of *point*."""
    if point.infinity:
        return point
    return Point(x=point.x, y=FIELD_PRIME - point.y)


def add(left: Point, right: Point) -> Point:
    """Return the sum of two points."""
    if left.infinity:
        return right
    if right.infinity:
        return left
    if left.x == right.x:
        if left.y != right.y:
            return Point(infinity=True)
        return double(left)

    x1, y1 = left.x, left.y
    x2, y2 = right.x, right.y
    slope = ((y2 - y1) * inverse(x2 - x1, FIELD_PRIME)) % FIELD_PRIME
    x3 = (slope * slope - x1 - x2) % FIELD_PRIME
    y3 = (slope * (x1 - x3) - y1) % FIELD_PRIME
    return Point(x=x3, y=y3)


def double(point: Point) -> Point:
    """Return ``2 * point``."""
    if point.infinity or point.y == 0:
        return Point(infinity=True)
    x1, y1 = point.x, point.y
    slope = ((3 * x1 * x1 + CURVE_A) * inverse(2 * y1, FIELD_PRIME)) % FIELD_PRIME
    x3 = (slope * slope - 2 * x1) % FIELD_PRIME
    y3 = (slope * (x1 - x3) - y1) % FIELD_PRIME
    return Point(x=x3, y=y3)


def multiply(scalar: int, point: Point) -> Point:
    """Return ``scalar * point`` via the Montgomery ladder."""
    if scalar == 0 or point.infinity:
        return Point(infinity=True)
    scalar = scalar % CURVE_ORDER
    if scalar == 0:
        return Point(infinity=True)

    r0 = Point(infinity=True)
    r1 = point
    for bit in bits(scalar):
        if bit == 0:
            r1 = add(r0, r1)
            r0 = double(r0)
        else:
            r0 = add(r0, r1)
            r1 = double(r1)
    return r0


def is_on_curve(point: Point) -> bool:
    """Return True if *point* lies on the secp256k1 curve."""
    if point.infinity:
        return True
    x, y = point.x, point.y
    return (y * y - (pow(x, 3, FIELD_PRIME) + CURVE_B)) % FIELD_PRIME == 0


# -- helpers --------------------------------------------------------------


def bits(scalar: int) -> list[int]:
    """Return the binary representation of *scalar* (MSB-first)."""
    if scalar == 0:
        return [0]
    return [int(b) for b in bin(scalar)[2:]]
