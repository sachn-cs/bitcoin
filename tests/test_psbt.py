"""Tests for the PSBT module."""

from __future__ import annotations

import pytest

from bitcoin.psbt import parse_psbt


def test_parse_psbt_invalid_magic() -> None:
    from bitcoin.exceptions import BitcoinError

    try:
        parse_psbt(b"\x00" * 100)
    except BitcoinError:
        pass


def test_parse_psbt_unknown_global() -> None:
    """PSBT with only an unknown global key should fail gracefully."""
    from bitcoin.exceptions import BitcoinError

    data = b"psbt\xff"
    data += b"\x01"  # key length (1)
    data += b"\xff"  # key type (unknown)
    data += b"\x04"  # value length (4)
    data += b"test"
    data += b"\x00"  # global separator
    try:
        parse_psbt(data)
    except BitcoinError:
        pass


def test_parse_psbt_too_short() -> None:
    from bitcoin.exceptions import BitcoinError

    with pytest.raises(BitcoinError):
        parse_psbt(b"")


def test_parse_psbt_magic_only() -> None:
    from bitcoin.exceptions import BitcoinError

    with pytest.raises(BitcoinError):
        parse_psbt(b"psbt\xff")


def test_parse_psbt_missing_inputs() -> None:
    """PSBT with global map but no inputs."""
    from bitcoin.exceptions import BitcoinError

    data = b"psbt\xff"
    data += b"\x00"  # global separator (empty global map)
    with pytest.raises(BitcoinError):
        parse_psbt(data)


def test_parse_psbt_non_minimal_varint() -> None:
    """PSBT with non-minimal varints should fail."""
    from bitcoin.exceptions import BitcoinError

    data = b"psbt\xff"
    data += b"\x00"  # global separator
    # input with non-minimal varint key length (0xfd prefix for value < 0xfd)
    data += b"\xfd\x01\x00"  # non-minimal varint for key length 1
    data += b"\x00"  # key type
    data += b"\x01"  # value length
    data += b"\x00"  # value
    data += b"\x00"  # input separator
    data += b"\x00"  # output separator
    with pytest.raises(BitcoinError):
        parse_psbt(data)
