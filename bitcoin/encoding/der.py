"""DER-encoded ECDSA signature parsing and serialization."""

from typing import Tuple


def encode_der(r: int, s: int, s_high_ok: bool = False) -> bytes:
    """Encode ``(r, s)`` as a DER signature.

    If *s_high_ok* is ``False`` (default) and *s* exceeds ``ORDER / 2``,
    *s* is negated.
    """
    from bitcoin.curve.params import CURVE_ORDER

    half_order = CURVE_ORDER // 2
    if not s_high_ok and s > half_order:
        s = CURVE_ORDER - s

    def _encode_int(value: int) -> bytes:
        raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
        if raw[0] & 0x80:
            raw = b"\x00" + raw
        return bytes([0x02, len(raw)]) + raw

    r_enc = _encode_int(r)
    s_enc = _encode_int(s)
    content = r_enc + s_enc
    return bytes([0x30, len(content)]) + content


def decode_der(sig: bytes) -> Tuple[int, int]:
    """Decode a DER-encoded signature to ``(r, s)``.

    Raises:
        ValueError: If the encoding is malformed.
    """
    if len(sig) < 6 or sig[0] != 0x30:
        raise ValueError("Not a valid DER signature.")

    offset = 2
    if sig[1] != len(sig) - 2:
        raise ValueError("Invalid DER sequence length.")

    r, offset = _decode_int(sig, offset)
    s, offset = _decode_int(sig, offset)

    if offset != len(sig):
        raise ValueError("Trailing data in DER signature.")

    return r, s


def _decode_int(data: bytes, offset: int) -> Tuple[int, int]:
    """Decode a DER INTEGER at *offset*; returns ``(value, new_offset)``."""
    if offset + 2 > len(data) or data[offset] != 0x02:
        raise ValueError("Invalid DER integer tag.")
    length = data[offset + 1]
    start = offset + 2
    end = start + length
    if end > len(data):
        raise ValueError("Truncated DER integer.")
    raw = data[start:end]
    if len(raw) > 1 and raw[0] == 0:
        raise ValueError("Unnecessary leading zero in DER integer.")
    value = int.from_bytes(raw, "big")
    return value, end
