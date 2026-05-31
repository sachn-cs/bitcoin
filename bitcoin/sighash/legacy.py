"""Legacy (pre-SegWit) sighash computation (BIP-143 predecessor)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bitcoin.encoding.hasher import hash256
from bitcoin.encoding.varint import encode_varint
from bitcoin.sighash.flag import SIGHASH_ANYONECANPAY, SIGHASH_MASK, SIGHASH_NONE, SIGHASH_SINGLE
from bitcoin.transaction.models import EMPTY_WITNESS

if TYPE_CHECKING:
    from bitcoin.transaction.models import Tx


def sighash_legacy(tx: Tx, input_index: int, script: bytes, flag: int) -> bytes:
    """Compute the legacy sighash for *tx* at *input_index*.

    This is the algorithm used before SegWit (BIP-143).
    """
    from bitcoin.services.serializer import _serialize_legacy_tx_for_sighash

    data = bytearray()
    data.extend(tx.version.to_bytes(4, "little"))

    if flag & SIGHASH_ANYONECANPAY:
        data.append(0x00)  # no inputs
    else:
        data.extend(encode_varint(len(tx.inputs)))
        for i, txin in enumerate(tx.inputs):
            if i == input_index:
                data.extend(txin.previous_output.txid)
                data.extend(txin.previous_output.vout.to_bytes(4, "little"))
                data.extend(encode_varint(len(script)))
                data.extend(script)
                data.extend(txin.sequence.to_bytes(4, "little"))
            else:
                data.extend(txin.previous_output.txid)
                data.extend(txin.previous_output.vout.to_bytes(4, "little"))
                data.append(0x00)  # empty script
                if (flag & SIGHASH_MASK) in (SIGHASH_NONE, SIGHASH_SINGLE):
                    data.extend(b"\x00\x00\x00\x00")  # sequence 0
                else:
                    data.extend(txin.sequence.to_bytes(4, "little"))

    if (flag & SIGHASH_MASK) == SIGHASH_NONE:
        data.extend(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")  # varint 0
    elif (flag & SIGHASH_MASK) == SIGHASH_SINGLE:
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
                # Missing outputs are serialized with max values per BIP
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

    return hash256(bytes(data))
