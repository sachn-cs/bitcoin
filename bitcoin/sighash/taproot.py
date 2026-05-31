"""Taproot (BIP-341) sighash computation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from bitcoin.encoding.hasher import tagged_hash

if TYPE_CHECKING:
    from bitcoin.transaction.models import Tx


def sighash_taproot(
    tx: Tx,
    input_index: int,
    script: Optional[bytes],
    flag: int,
    *,
    extension: bytes = b"",
    tapleaf_hash: Optional[bytes] = None,
    key_version: int = 0,
    codeseparator_position: int = 0xFFFFFFFF,
    annex: Optional[bytes] = None,
) -> bytes:
    """Compute the BIP-341 Taproot sighash.

    Arguments:
        tx: The transaction.
        input_index: Index of the input being signed.
        script: The script being executed (``None`` for key path).
        flag: SIGHASH flag (only 0x00 for default, or 0x01–0x83).
        extension: Extra data for future extensions (default ``b""``).
        tapleaf_hash: Hash of the tapleaf (required for script path).
        key_version: Key version (0 for current).
        codeseparator_position: Last ``OP_CODESEPARATOR`` position.
        annex: Optional annex data.
    """
    from bitcoin.services.serializer import _serialize_tx_for_sighash_taproot

    data = bytearray()
    # Hash type
    data.extend(flag.to_bytes(1, "little"))
    data.extend(extension)

    # Epoch (0 for current)
    data.extend((0).to_bytes(1, "little"))

    # Control block
    if input_index >= len(tx.inputs):
        raise IndexError("Input index out of range.")
    inp = tx.inputs[input_index]
    data.extend(inp.previous_output.txid)
    data.extend(inp.previous_output.vout.to_bytes(4, "little"))
    data.extend(inp.sequence.to_bytes(4, "little"))

    # Script path details
    if script is not None:
        if tapleaf_hash is None:
            raise ValueError("tapleaf_hash required for script-path signing.")
        data.extend((1).to_bytes(1, "little"))  # script path
        data.extend(tapleaf_hash)
        data.extend(key_version.to_bytes(1, "little"))
        data.extend(codeseparator_position.to_bytes(4, "little"))
    else:
        data.extend((0).to_bytes(1, "little"))  # key path

    # Annex
    if annex is not None:
        data.extend((1).to_bytes(1, "little"))
        data.extend(annex)
    else:
        data.extend((0).to_bytes(1, "little"))

    # Serialize remaining transaction data for sighash
    data.extend(_serialize_tx_for_sighash_taproot(tx, flag))

    # Script (if present)
    if script is not None:
        data.extend(encode_varint(len(script)))
        data.extend(script)

    return tagged_hash("TapSighash", bytes(data))


def encode_varint(value: int) -> bytes:
    """Minimal varint helper for the module's self-containment."""
    if value < 0xFD:
        return value.to_bytes(1, "little")
    if value <= 0xFFFF:
        return b"\xfd" + value.to_bytes(2, "little")
    if value <= 0xFFFFFFFF:
        return b"\xfe" + value.to_bytes(4, "little")
    return b"\xff" + value.to_bytes(8, "little")
