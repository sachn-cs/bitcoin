"""The :class:`Point` value type — a point on the secp256k1 curve."""

from __future__ import annotations

from bitcoin.curve.params import CURVE_B, FIELD_PRIME


class Point:
    """An affine point on secp256k1, or the point at infinity.

    Slots are used for a compact memory layout.  The point is guaranteed
    to lie on the curve when *infinity* is ``False``.
    """

    __slots__ = ("_x", "_y", "_infinity")

    def __init__(self, x: int | None = None, y: int | None = None,
                 *, infinity: bool = False) -> None:
        if infinity:
            self._x: int | None = None
            self._y: int | None = None
            self._infinity: bool = True
            return
        if x is None or y is None:
            raise ValueError("Affine point requires both x and y.")
        if not (0 <= x < FIELD_PRIME):
            raise ValueError(f"x coordinate out of field: {x}")
        if not (0 <= y < FIELD_PRIME):
            raise ValueError(f"y coordinate out of field: {y}")
        self._x = x
        self._y = y
        self._infinity = False

    # -- read-only properties ------------------------------------------------

    @property
    def x(self) -> int | None:
        return self._x

    @property
    def y(self) -> int | None:
        return self._y

    @property
    def infinity(self) -> bool:
        return self._infinity

    # -- equality / hashing --------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        if self._infinity and other._infinity:
            return True
        if self._infinity != other._infinity:
            return False
        return self._x == other._x and self._y == other._y

    def __hash__(self) -> int:
        if self._infinity:
            return hash((True,))
        return hash((False, self._x, self._y))

    def __repr__(self) -> str:
        if self._infinity:
            return "Point(infinity=True)"
        return f"Point(x=0x{self._x:064x}, y=0x{self._y:064x})"

    # -- constructors --------------------------------------------------------

    @classmethod
    def from_sec_compressed(cls, data: bytes) -> Point:
        """Parse a 33-byte compressed SEC key."""
        if len(data) != 33 or data[0] not in (0x02, 0x03):
            raise ValueError("Invalid compressed SEC key.")
        x = int.from_bytes(data[1:33], "big")
        y_sq = (pow(x, 3, FIELD_PRIME) + CURVE_B) % FIELD_PRIME
        y = pow(y_sq, (FIELD_PRIME + 1) // 4, FIELD_PRIME)
        if (y & 1) != (data[0] & 1):
            y = FIELD_PRIME - y
        return cls(x=x, y=y)

    @classmethod
    def from_sec_uncompressed(cls, data: bytes) -> Point:
        """Parse a 65-byte uncompressed SEC key."""
        if len(data) != 65 or data[0] != 0x04:
            raise ValueError("Invalid uncompressed SEC key.")
        x = int.from_bytes(data[1:33], "big")
        y = int.from_bytes(data[33:], "big")
        return cls(x=x, y=y)

    # -- serialization -------------------------------------------------------

    def to_sec_compressed(self) -> bytes:
        """Encode as a 33-byte compressed SEC key."""
        prefix = bytes([0x02 | (self._y & 1)])
        return prefix + self._x.to_bytes(32, "big")

    def to_sec_uncompressed(self) -> bytes:
        """Encode as a 65-byte uncompressed SEC key."""
        return b"\x04" + self._x.to_bytes(32, "big") + self._y.to_bytes(32, "big")
