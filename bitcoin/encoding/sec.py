"""SEC-format public-key parsing and serialization."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcoin.curve.point import Point


def parse_sec(data: bytes) -> "Point":
    """Parse a SEC-encoded public key into a ``Point``.

    Supports both compressed (33-byte) and uncompressed (65-byte) formats.

    Raises:
        ValueError: If the data is malformed or the point is not on the curve.
    """
    from bitcoin.curve.point import Point

    if len(data) == 33 and data[0] in (0x02, 0x03):
        point = Point.from_sec_compressed(data)
    elif len(data) == 65 and data[0] == 0x04:
        point = Point.from_sec_uncompressed(data)
    else:
        raise ValueError(
            f"Invalid SEC key length {len(data)} (expected 33 or 65 bytes)."
        )

    from bitcoin.curve.operations import is_on_curve

    if not is_on_curve(point):
        raise ValueError("Decoded point is not on the secp256k1 curve.")
    return point


def serialize_sec(point: "Point", compressed: bool = True) -> bytes:
    """Serialize a ``Point`` to SEC format.

    Raises:
        ValueError: If the point is at infinity.
    """
    if point.infinity:
        raise ValueError("Cannot serialize point at infinity.")
    if compressed:
        return point.to_sec_compressed()
    return point.to_sec_uncompressed()
