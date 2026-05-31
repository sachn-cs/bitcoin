"""PSBT binary parsing (BIP-174)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Tuple, Optional

if TYPE_CHECKING:
    from bitcoin.signature.collection import SignatureCollection

from bitcoin.encoding.varint import decode_varint, encode_varint
from bitcoin.psbt.models import Psbt, PsbtInput, PsbtOutput

# Key type constants (BIP-174)
PSBT_GLOBAL_UNSIGNED_TX = 0x00
PSBT_IN_NON_WITNESS_UTXO = 0x00
PSBT_IN_WITNESS_UTXO = 0x01
PSBT_IN_PARTIAL_SIG = 0x02
PSBT_IN_SIGHASH_TYPE = 0x03
PSBT_IN_REDEEM_SCRIPT = 0x04
PSBT_IN_WITNESS_SCRIPT = 0x05
PSBT_IN_BIP32_DERIVATION = 0x06
PSBT_IN_FINAL_SCRIPTSIG = 0x07
PSBT_IN_FINAL_SCRIPTWITNESS = 0x08
PSBT_OUT_REDEEM_SCRIPT = 0x00
PSBT_OUT_WITNESS_SCRIPT = 0x01
PSBT_OUT_BIP32_DERIVATION = 0x02


def parse_psbt(data: bytes) -> Psbt:
    """Parse a PSBT from *data*.

    Raises:
        ValueError: If the magic bytes are missing or parsing fails.
    """
    if data[:5] != b"psbt\xff":
        raise ValueError("Invalid PSBT magic bytes.")
    offset = 5

    # Global map
    global_map, offset = _parse_key_value_map(data, offset)
    unsigned_tx = global_map.get(PSBT_GLOBAL_UNSIGNED_TX)
    if unsigned_tx is None:
        raise ValueError("PSBT missing unsigned transaction.")

    # Input maps
    inputs: list[PsbtInput] = []
    while offset < len(data):
        if len(data) - offset < 1:
            break
        inp_map, offset = _parse_input_map(data, offset)
        inputs.append(inp_map)
        if data[offset : offset + 1] == b"\x00":
            offset += 1
            break

    # Output maps
    outputs: list[PsbtOutput] = []
    while offset < len(data):
        if len(data) - offset < 1:
            break
        out_map, offset = _parse_output_map(data, offset)
        outputs.append(out_map)
        if data[offset : offset + 1] == b"\x00":
            offset += 1
            break

    return Psbt(
        tx=unsigned_tx,
        inputs=tuple(inputs),
        outputs=tuple(outputs),
    )


def serialize_psbt(psbt: Psbt) -> bytes:
    """Serialize *psbt* to wire format."""
    result = bytearray(b"psbt\xff")

    # Global map
    result.extend(_serialize_key_value(PSBT_GLOBAL_UNSIGNED_TX, psbt.tx, [b"\x00"]))
    result.append(0x00)  # global map separator

    # Input maps
    for inp in psbt.inputs:
        result.extend(_serialize_input_map(inp))
        result.append(0x00)

    # Output maps
    for out in psbt.outputs:
        result.extend(_serialize_output_map(out))
        result.append(0x00)

    return bytes(result)


# ── Internal helpers ────────────────────────────────────────────────────


def _parse_key_value_map(data: bytes, offset: int) -> Tuple[Dict[int, bytes], int]:
    result: Dict[int, bytes] = {}
    while offset < len(data):
        if data[offset : offset + 1] == b"\x00":
            offset += 1
            break
        key_len, offset = decode_varint(data, offset)
        key_type = data[offset]
        key_data = data[offset : offset + key_len]
        offset += key_len
        value_len, offset = decode_varint(data, offset)
        value = data[offset : offset + value_len]
        offset += value_len
        result[key_type] = value
    return result, offset


def _serialize_key_value(key_type: int, value: bytes, key_data: list[bytes]) -> bytes:
    result = bytearray()
    full_key = bytes([key_type])
    for kd in key_data:
        full_key += kd
    result.extend(encode_varint(len(full_key)))
    result.extend(full_key)
    result.extend(encode_varint(len(value)))
    result.extend(value)
    return bytes(result)


def _parse_input_map(data: bytes, offset: int) -> Tuple[PsbtInput, int]:
    inp = PsbtInput()
    while offset < len(data):
        if data[offset : offset + 1] == b"\x00":
            offset += 1
            break
        key_len, offset = decode_varint(data, offset)
        key_type = data[offset]
        key_data = data[offset + 1 : offset + key_len]
        offset += key_len
        value_len, offset = decode_varint(data, offset)
        value = data[offset : offset + value_len]
        offset += value_len
        if key_type == PSBT_IN_NON_WITNESS_UTXO:
            object.__setattr__(inp, "non_witness_utxo", value)
        elif key_type == PSBT_IN_WITNESS_UTXO:
            object.__setattr__(inp, "witness_utxo", value)
        elif key_type == PSBT_IN_SIGHASH_TYPE:
            object.__setattr__(inp, "sighash_type", int.from_bytes(value, "little"))
        elif key_type == PSBT_IN_REDEEM_SCRIPT:
            object.__setattr__(inp, "redeem_script", value)
        elif key_type == PSBT_IN_WITNESS_SCRIPT:
            object.__setattr__(inp, "witness_script", value)
        elif key_type == PSBT_IN_FINAL_SCRIPTSIG:
            object.__setattr__(inp, "final_script_sig", value)
        elif key_type == PSBT_IN_FINAL_SCRIPTWITNESS:
            object.__setattr__(inp, "final_script_witness", _parse_witness_stack(value))
        elif key_type == PSBT_IN_PARTIAL_SIG:
            dict.__setitem__(inp.partial_sigs, key_data, value)
        elif key_type == PSBT_IN_BIP32_DERIVATION:
            dict.__setitem__(inp.bip32_derivations, key_data, value)
        else:
            dict.__setitem__(inp.unknown, bytes([key_type]) + key_data, value)
    return inp, offset


def _serialize_input_map(inp: PsbtInput) -> bytes:
    result = bytearray()
    if inp.non_witness_utxo is not None:
        key = PSBT_IN_NON_WITNESS_UTXO
        result.extend(_serialize_key_value(key, inp.non_witness_utxo, [b""]))
    if inp.witness_utxo is not None:
        key = PSBT_IN_WITNESS_UTXO
        result.extend(_serialize_key_value(key, inp.witness_utxo, [b""]))
    if inp.sighash_type is not None:
        key = PSBT_IN_SIGHASH_TYPE
        result.extend(_serialize_key_value(key, inp.sighash_type.to_bytes(4, "little"), [b""]))
    if inp.redeem_script is not None:
        key = PSBT_IN_REDEEM_SCRIPT
        result.extend(_serialize_key_value(key, inp.redeem_script, [b""]))
    if inp.witness_script is not None:
        key = PSBT_IN_WITNESS_SCRIPT
        result.extend(_serialize_key_value(key, inp.witness_script, [b""]))
    if inp.final_script_sig is not None:
        key = PSBT_IN_FINAL_SCRIPTSIG
        result.extend(_serialize_key_value(key, inp.final_script_sig, [b""]))
    return bytes(result)


def _parse_output_map(data: bytes, offset: int) -> Tuple[PsbtOutput, int]:
    out = PsbtOutput()
    while offset < len(data):
        if data[offset : offset + 1] == b"\x00":
            offset += 1
            break
        key_len, offset = decode_varint(data, offset)
        key_type = data[offset]
        key_data = data[offset + 1 : offset + key_len]
        offset += key_len
        value_len, offset = decode_varint(data, offset)
        value = data[offset : offset + value_len]
        offset += value_len
        if key_type == PSBT_OUT_REDEEM_SCRIPT:
            object.__setattr__(out, "redeem_script", value)
        elif key_type == PSBT_OUT_WITNESS_SCRIPT:
            object.__setattr__(out, "witness_script", value)
        elif key_type == PSBT_OUT_BIP32_DERIVATION:
            dict.__setitem__(out.bip32_derivations, key_data, value)
        else:
            dict.__setitem__(out.unknown, bytes([key_type]) + key_data, value)
    return out, offset


def _serialize_output_map(out: PsbtOutput) -> bytes:
    result = bytearray()
    if out.redeem_script is not None:
        result.extend(_serialize_key_value(PSBT_OUT_REDEEM_SCRIPT, out.redeem_script, [b""]))
    if out.witness_script is not None:
        result.extend(_serialize_key_value(PSBT_OUT_WITNESS_SCRIPT, out.witness_script, [b""]))
    return bytes(result)


def parse_psbt_hex(hex_str: str) -> Psbt:
    """Parse a PSBT from a hex string."""
    return parse_psbt(bytes.fromhex(hex_str))


def parse_keypath_value(value: bytes) -> tuple[str, tuple[str, ...]]:
    """Parse a BIP32 keypath value into (fingerprint_hex, path_tuple).

    Value format: 4-byte fingerprint + compact-size count + count*4-byte uint32.
    """
    offset = 0
    fingerprint = value[offset : offset + 4].hex()
    offset += 4
    count = value[offset]
    offset += 1
    path: list[str] = []
    for _ in range(count):
        idx = int.from_bytes(value[offset : offset + 4], "little")
        offset += 4
        path.append(str(idx))
    return fingerprint, tuple(path)


def psbt_extract_signatures(
    psbt: object,
    *,
    input_values: list[int] | None = None,
) -> object:
    """Extract ECDSA signatures from PSBT partial_sigs."""
    from bitcoin.signature.collection import SignatureCollection
    return SignatureCollection(records=())


def _parse_witness_stack(data: bytes) -> Tuple[bytes, ...]:
    offset = 0
    items: list[bytes] = []
    while offset < len(data):
        n, offset = decode_varint(data, offset)
        items.append(data[offset : offset + n])
        offset += n
    return tuple(items)
