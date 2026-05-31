"""Binary serialization helpers."""

from typing import Iterator


def bytes_to_int(data: bytes, byteorder: str = "big") -> int:
    """Convert *data* to an integer.

    Raises:
        TypeError: If *data* is not ``bytes`` or *byteorder* is not ``str``.
        ValueError: If *byteorder* is not ``'big'`` or ``'little'``.
    """
    return int.from_bytes(data, byteorder)


def int_to_bytes(value: int, length: int, byteorder: str = "big") -> bytes:
    """Convert *value* to a fixed-length byte string.

    Raises:
        TypeError: If *value* is not ``int``.
        ValueError: If *value* is negative or out of range.
    """
    return value.to_bytes(length, byteorder)


def read_exactly(stream: bytes, n: int, offset: int = 0) -> tuple[bytes, int]:
    """Read exactly *n* bytes from *stream* at *offset*.

    Raises:
        ValueError: If fewer than *n* bytes are available.
    """
    if offset + n > len(stream):
        raise ValueError(
            f"Requested {n} bytes at offset {offset} but stream only "
            f"has {len(stream)} bytes."
        )
    return stream[offset : offset + n], offset + n


def iter_bytes(data: bytes, chunk_size: int) -> Iterator[bytes]:
    """Yield *chunk_size*-sized slices of *data*."""
    for i in range(0, len(data), chunk_size):
        yield data[i : i + chunk_size]
