"""SIGHASH flag constants."""

from __future__ import annotations

SIGHASH_ALL = 0x01
SIGHASH_NONE = 0x02
SIGHASH_SINGLE = 0x03
SIGHASH_ANYONECANPAY = 0x80
SIGHASH_MASK = 0x1F
SIGHASH_ALL_ANYONECANPAY = SIGHASH_ALL | SIGHASH_ANYONECANPAY
SIGHASH_NONE_ANYONECANPAY = SIGHASH_NONE | SIGHASH_ANYONECANPAY
SIGHASH_SINGLE_ANYONECANPAY = SIGHASH_SINGLE | SIGHASH_ANYONECANPAY

SIGHASH_NAMES: dict[int, str] = {
    SIGHASH_ALL: "SIGHASH_ALL",
    SIGHASH_NONE: "SIGHASH_NONE",
    SIGHASH_SINGLE: "SIGHASH_SINGLE",
    SIGHASH_ALL_ANYONECANPAY: "SIGHASH_ALL|ANYONECANPAY",
    SIGHASH_NONE_ANYONECANPAY: "SIGHASH_NONE|ANYONECANPAY",
    SIGHASH_SINGLE_ANYONECANPAY: "SIGHASH_SINGLE|ANYONECANPAY",
}


def sighash_name(flag: int) -> str:
    """Return a human-readable name for *flag*."""
    base = flag & SIGHASH_MASK
    has_acp = bool(flag & SIGHASH_ANYONECANPAY)
    if has_acp:
        base |= SIGHASH_ANYONECANPAY
    return SIGHASH_NAMES.get(base, f"SIGHASH_UNKNOWN({flag})")


def require_sighash_flag(flag: int) -> int:
    """Validate and return the standardised sighash flag.

    Raises:
        ValueError: If the flag is out of range.
    """
    base = flag & SIGHASH_MASK
    if base not in (SIGHASH_ALL, SIGHASH_NONE, SIGHASH_SINGLE):
        raise ValueError(f"Unknown SIGHASH base type: {base}.")
    return flag
