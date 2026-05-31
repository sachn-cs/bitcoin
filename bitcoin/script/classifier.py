"""Script-type classification (P2PK, P2PKH, P2WPKH, P2SH, P2TR, etc.)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from bitcoin.script.opcodes import (
    OP_0,
    OP_1,
    OP_16,
    OP_CHECKSIG,
    OP_DUP,
    OP_EQUALVERIFY,
    OP_HASH160,
)

if TYPE_CHECKING:
    from bitcoin.script.parser import Push

# Script type identifiers
P2PK = "p2pk"
P2PKH = "p2pkh"
P2SH = "p2sh"
P2WPKH = "p2wpkh"
P2WSH = "p2wsh"
P2TR = "p2tr"
NULL_DATA = "null_data"
NONSTANDARD = "nonstandard"


def classify_script_pubkey(script_pubkey: list) -> str:
    """Return the type of *script_pubkey* (a list of script elements)."""
    if not script_pubkey:
        return NONSTANDARD

    # Null data (OP_RETURN)
    if script_pubkey[0] == 0x6A:
        return NULL_DATA

    # P2PK: <pubkey> OP_CHECKSIG
    if len(script_pubkey) == 2 and script_pubkey[-1] == OP_CHECKSIG:
        if isinstance(script_pubkey[0], bytes) and len(script_pubkey[0]) in (
            33,
            65,
        ):
            return P2PK

    # P2PKH: OP_DUP OP_HASH160 <20-byte hash> OP_EQUALVERIFY OP_CHECKSIG
    if (
        len(script_pubkey) == 5
        and script_pubkey[0] == OP_DUP
        and script_pubkey[1] == OP_HASH160
        and isinstance(script_pubkey[2], bytes)
        and len(script_pubkey[2]) == 20
        and script_pubkey[3] == OP_EQUALVERIFY
        and script_pubkey[4] == OP_CHECKSIG
    ):
        return P2PKH

    # P2SH: OP_HASH160 <20-byte hash> OP_EQUAL
    if (
        len(script_pubkey) == 3
        and script_pubkey[0] == OP_HASH160
        and isinstance(script_pubkey[1], bytes)
        and len(script_pubkey[1]) == 20
        and script_pubkey[2] == 0x87
    ):
        return P2SH

    # Native SegWit templates
    if _is_segwit_template(script_pubkey):
        witness_version = _segwit_version(script_pubkey)
        push = script_pubkey[1]
        if witness_version == 0:
            if isinstance(push, bytes) and len(push) == 20:
                return P2WPKH
            if isinstance(push, bytes) and len(push) == 32:
                return P2WSH
        if witness_version == 1:
            if isinstance(push, bytes) and len(push) == 32:
                return P2TR

    return NONSTANDARD


def _is_segwit_template(elements: list) -> bool:
    """Return True if *elements* looks like a SegWit output::

        <version_0..16> <push>
    """
    if len(elements) != 2:
        return False
    ver = elements[0]
    if isinstance(ver, int) and OP_0 <= ver <= OP_16:
        return isinstance(elements[1], bytes) and len(elements[1]) >= 2
    return False


def _segwit_version(elements: list) -> int:
    v = elements[0]
    if isinstance(v, int):
        if v == OP_0:
            return 0
        if OP_1 <= v <= OP_16:
            return v - OP_1 + 1
    return -1


def is_witness_program(script: bytes, version: int = 0) -> bool:
    """Return whether the script is a SegWit witness program of the given version."""
    if len(script) not in {22, 34}:
        return False
    if script[0] != version:
        return False
    if len(script) == 22:
        return script[1] == 20
    return script[1] == 32


def witness_program_hash_size(script: bytes) -> int | None:
    """Return the hash size of a witness program, or None if not a witness program."""
    if not is_witness_program(script):
        return None
    return script[1]


def is_p2pkh_pushes(pushes: list[bytes]) -> bool:
    """Return whether the pushes match a P2PKH pattern (signature + public key)."""
    return len(pushes) == 2 and len(pushes[1]) in {33, 65}


def is_taproot(script: bytes) -> bool:
    """Return whether the script is a Taproot output (OP_1 <32-byte push>)."""
    return len(script) == 34 and script[0] == 0x51 and script[1] == 0x20


def is_taproot_script_path(witness_items: list[bytes]) -> bool:
    """Return whether the witness stack indicates a Taproot script path spend."""
    if len(witness_items) < 2:
        return False
    if len(witness_items[-1]) >= 10000:
        return False
    script_item = witness_items[-2]
    if not script_item:
        return False
    return 0x50 <= script_item[0] <= 0x5F


def classify_script_sig(script_sig: list) -> str:
    """Classify a scriptSig based on its contents."""
    if not script_sig:
        return "empty"
    return "nonstandard"
