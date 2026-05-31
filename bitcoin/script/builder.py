"""Script building helpers."""

from __future__ import annotations

from bitcoin.script.opcodes import (
    OP_CHECKSIG,
    OP_DUP,
    OP_EQUALVERIFY,
    OP_HASH160,
    OP_0,
    OP_1,
)

from bitcoin.script.parser import serialize_script
from bitcoin.encoding.hasher import hash160


def build_p2pk(pubkey_bytes: bytes) -> bytes:
    """Build a P2PK output script."""
    return serialize_script([pubkey_bytes, OP_CHECKSIG])


def build_p2pkh(hash160_bytes: bytes) -> bytes:
    """Build a P2PKH output script."""
    if len(hash160_bytes) != 20:
        raise ValueError("P2PKH requires a 20-byte hash.")
    return serialize_script([OP_DUP, OP_HASH160, hash160_bytes, OP_EQUALVERIFY, OP_CHECKSIG])


def build_p2wpkh(hash160_bytes: bytes) -> bytes:
    """Build a P2WPKH witness program."""
    if len(hash160_bytes) != 20:
        raise ValueError("P2WPKH requires a 20-byte hash.")
    return serialize_script([OP_0, hash160_bytes])


def build_p2wsh(sha256_bytes: bytes) -> bytes:
    """Build a P2WSH witness program."""
    if len(sha256_bytes) != 32:
        raise ValueError("P2WSH requires a 32-byte hash.")
    return serialize_script([OP_0, sha256_bytes])


def build_p2tr(x_only_bytes: bytes) -> bytes:
    """Build a P2TR (Taproot) output script."""
    if len(x_only_bytes) != 32:
        raise ValueError("P2TR requires a 32-byte x-only public key.")
    return serialize_script([OP_1, x_only_bytes])


def make_p2pkh_script(pubkey: bytes) -> bytes:
    """Build a P2PKH scriptPubKey from a public key."""
    digest = hash160(pubkey)
    return b"\x76\xa9\x14" + digest + b"\x88\xac"
