"""Transaction binary parsing."""

from __future__ import annotations

from typing import List, Tuple

from bitcoin.encoding.varint import decode_varint
from bitcoin.transaction.models import OutPoint, TxIn, TxOut, Tx, Witness


def parse_tx(data: bytes, offset: int = 0) -> Tuple[Tx, int]:
    """Deserialize a transaction from *data* starting at *offset*.

    Returns ``(Tx, new_offset)``.
    """
    version = int.from_bytes(data[offset : offset + 4], "little")
    offset += 4

    # Check for SegWit marker (0x00 0x01)
    is_segwit = data[offset : offset + 2] == b"\x00\x01"
    if is_segwit:
        offset += 2

    inputs, offset = _parse_inputs(data, offset, is_segwit)
    outputs, offset = _parse_outputs(data, offset)

    if is_segwit:
        inputs = list(inputs)
        for i in range(len(inputs)):
            witness, offset = _parse_witness(data, offset)
            inputs[i] = TxIn(
                previous_output=inputs[i].previous_output,
                script_sig=inputs[i].script_sig,
                sequence=inputs[i].sequence,
                witness=witness,
            )
        inputs = tuple(inputs)

    lock_time = int.from_bytes(data[offset : offset + 4], "little")
    offset += 4

    return Tx(version=version, inputs=tuple(inputs), outputs=tuple(outputs), lock_time=lock_time), offset


def _parse_inputs(data: bytes, offset: int, is_segwit: bool) -> Tuple[List[TxIn], int]:
    n, offset = decode_varint(data, offset)
    inputs: List[TxIn] = []
    for _ in range(n):
        txid = data[offset : offset + 32]
        offset += 32
        vout = int.from_bytes(data[offset : offset + 4], "little")
        offset += 4
        script_len, offset = decode_varint(data, offset)
        script_sig = data[offset : offset + script_len]
        offset += script_len
        sequence = int.from_bytes(data[offset : offset + 4], "little")
        offset += 4
        inputs.append(
            TxIn(
                previous_output=OutPoint(txid=txid, vout=vout),
                script_sig=script_sig,
                sequence=sequence,
                witness=Witness(()),
            )
        )
    return inputs, offset


def _parse_outputs(data: bytes, offset: int) -> Tuple[List[TxOut], int]:
    n, offset = decode_varint(data, offset)
    outputs: List[TxOut] = []
    for _ in range(n):
        value = int.from_bytes(data[offset : offset + 8], "little")
        offset += 8
        script_len, offset = decode_varint(data, offset)
        script_pubkey = data[offset : offset + script_len]
        offset += script_len
        outputs.append(TxOut(value=value, script_pubkey=script_pubkey))
    return outputs, offset


def _parse_witness(data: bytes, offset: int) -> Tuple[Witness, int]:
    n, offset = decode_varint(data, offset)
    items: list[bytes] = []
    for _ in range(n):
        item_len, offset = decode_varint(data, offset)
        item = data[offset : offset + item_len]
        offset += item_len
        items.append(item)
    return Witness(tuple(items)), offset
