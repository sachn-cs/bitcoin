"""Hexadecimal encoding/decoding helpers."""

_HEX_CHARS = b"0123456789abcdef"


def encode_hex(data: bytes) -> str:
    """Return the hex representation of *data*.

    Raises:
        TypeError: If *data* is not ``bytes``.
    """
    return data.hex()


def decode_hex(hex_str: str) -> bytes:
    """Decode a hex string to bytes.

    Raises:
        TypeError: If *hex_str* is not ``str``.
        ValueError: If the string has an odd length or contains invalid chars.
    """
    return bytes.fromhex(hex_str)
