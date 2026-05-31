"""Transaction serialization to wire format."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bitcoin.encoding.varint import encode_varint

if TYPE_CHECKING:
    from bitcoin.transaction.models import Tx


def serialize_tx(tx: Tx) -> bytes:
    """Serialize *tx* to wire format (SegWit-aware)."""
    data = bytearray()
    data.extend(tx.version.to_bytes(4, "little"))

    if tx.is_segwit():
        data.extend(b"\x00\x01")  # SegWit marker + flag

    data.extend(encode_varint(len(tx.inputs)))
    for txin in tx.inputs:
        data.extend(txin.previous_output.txid)
        data.extend(txin.previous_output.vout.to_bytes(4, "little"))
        data.extend(encode_varint(len(txin.script_sig)))
        data.extend(txin.script_sig)
        data.extend(txin.sequence.to_bytes(4, "little"))

    data.extend(encode_varint(len(tx.outputs)))
    for txout in tx.outputs:
        data.extend(txout.value.to_bytes(8, "little"))
        data.extend(encode_varint(len(txout.script_pubkey)))
        data.extend(txout.script_pubkey)

    if tx.is_segwit():
        for txin in tx.inputs:
            data.extend(encode_varint(len(txin.witness)))
            for item in txin.witness.items:
                data.extend(encode_varint(len(item)))
                data.extend(item)

    data.extend(tx.lock_time.to_bytes(4, "little"))
    return bytes(data)


def serialize_legacy_tx(tx: Tx) -> bytes:
    """Serialize *tx* in legacy (non-SegWit) format — witness is ignored."""
    data = bytearray()
    data.extend(tx.version.to_bytes(4, "little"))
    data.extend(encode_varint(len(tx.inputs)))
    for txin in tx.inputs:
        data.extend(txin.previous_output.txid)
        data.extend(txin.previous_output.vout.to_bytes(4, "little"))
        data.extend(encode_varint(len(txin.script_sig)))
        data.extend(txin.script_sig)
        data.extend(txin.sequence.to_bytes(4, "little"))
    data.extend(encode_varint(len(tx.outputs)))
    for txout in tx.outputs:
        data.extend(txout.value.to_bytes(8, "little"))
        data.extend(encode_varint(len(txout.script_pubkey)))
        data.extend(txout.script_pubkey)
    data.extend(tx.lock_time.to_bytes(4, "little"))
    return bytes(data)


def _serialize_legacy_tx_for_sighash(tx: Tx, input_index: int, script: bytes, flag: int) -> bytes:
    """Legacy sighash serialization.  Called from ``sighash.legacy``."""
    from bitcoin.sighash.flag import SIGHASH_ANYONECANPAY, SIGHASH_MASK, SIGHASH_NONE, SIGHASH_SINGLE

    data = bytearray()
    data.extend(tx.version.to_bytes(4, "little"))

    if flag & SIGHASH_ANYONECANPAY:
        data.extend(encode_varint(1))
        txin = tx.inputs[input_index]
        data.extend(txin.previous_output.txid)
        data.extend(txin.previous_output.vout.to_bytes(4, "little"))
        data.extend(encode_varint(len(script)))
        data.extend(script)
        data.extend(txin.sequence.to_bytes(4, "little"))
    else:
        data.extend(encode_varint(len(tx.inputs)))
        for i, txin in enumerate(tx.inputs):
            data.extend(txin.previous_output.txid)
            data.extend(txin.previous_output.vout.to_bytes(4, "little"))
            if i == input_index:
                data.extend(encode_varint(len(script)))
                data.extend(script)
                data.extend(txin.sequence.to_bytes(4, "little"))
            else:
                if flag & SIGHASH_NONE or flag & SIGHASH_SINGLE:
                    data.append(0x00)  # empty script
                    data.extend(b"\x00\x00\x00\x00")
                else:
                    data.append(0x00)
                    data.extend(txin.sequence.to_bytes(4, "little"))

    base_flag = flag & SIGHASH_MASK
    if base_flag == SIGHASH_NONE:
        data.extend(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
    elif base_flag == SIGHASH_SINGLE:
        if input_index >= len(tx.outputs):
            raise ValueError("Input index out of bounds for SIGHASH_SINGLE.")
        data.extend(encode_varint(input_index + 1))
        for i in range(input_index + 1):
            if i < len(tx.outputs):
                out = tx.outputs[i]
                data.extend(out.value.to_bytes(8, "little"))
                data.extend(encode_varint(len(out.script_pubkey)))
                data.extend(out.script_pubkey)
            else:
                data.extend((0xFFFFFFFFFFFFFFFF).to_bytes(8, "little"))
                data.append(0x00)
    else:
        data.extend(encode_varint(len(tx.outputs)))
        for out in tx.outputs:
            data.extend(out.value.to_bytes(8, "little"))
            data.extend(encode_varint(len(out.script_pubkey)))
            data.extend(out.script_pubkey)

    data.extend(tx.lock_time.to_bytes(4, "little"))
    data.extend(flag.to_bytes(4, "little"))
    return bytes(data)


def _serialize_tx_for_sighash_taproot(tx: Tx, flag: int) -> bytes:
    """Serialization helper for BIP-341 sighash.  Called from ``sighash.taproot``."""
    data = bytearray()
    data.extend(encode_varint(len(tx.inputs)))
    for txin in tx.inputs:
        data.extend(txin.previous_output.txid)
        data.extend(txin.previous_output.vout.to_bytes(4, "little"))
        data.extend(txin.sequence.to_bytes(4, "little"))
    data.extend(encode_varint(len(tx.outputs)))
    for txout in tx.outputs:
        data.extend(txout.value.to_bytes(8, "little"))
        data.extend(encode_varint(len(txout.script_pubkey)))
        data.extend(txout.script_pubkey)
    return bytes(data)
