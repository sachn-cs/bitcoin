"""Core signature extraction engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from bitcoin.encoding.der import decode_der
from bitcoin.sighash.flag import (
    SIGHASH_ALL,
    SIGHASH_ANYONECANPAY,
    SIGHASH_NONE,
    SIGHASH_SINGLE,
    SIGHASH_MASK,
)
from bitcoin.signature.check import recover_public_key
from bitcoin.signature.record import Record
from bitcoin.script.classifier import (
    P2PK,
    P2PKH,
    P2SH,
    P2WPKH,
    P2WSH,
    P2TR,
    classify_script_pubkey,
)
from bitcoin.script.parser import parse_script

if TYPE_CHECKING:
    from bitcoin.transaction.models import Tx
    from bitcoin.curve.point import Point


def extract_signatures(
    tx: Tx,
    utxo_script_pubkeys: list[bytes] | None = None,
    utxo_values: list[int] | None = None,
) -> list[Record]:
    """Extract all ECDSA signatures from *tx*.

    Arguments:
        tx: The transaction to extract from.
        utxo_script_pubkeys: The ``scriptPubKey`` of each UTXO being spent.
            Required for P2SH, P2WPKH, P2WSH, and P2TR.
        utxo_values: The value (in satoshis) of each UTXO being spent.
            Required for SegWit inputs.

    Returns:
        A list of ``Record`` — one per extracted signature.

    Raises:
        ValueError: If required UTXO data is missing.
    """
    records: list[Record] = []

    for vin, txin in enumerate(tx.inputs):
        parsed_sig = parse_script(txin.script_sig) if txin.script_sig else []
        script_pubkey = utxo_script_pubkeys[vin] if utxo_script_pubkeys else b""
        value = utxo_values[vin] if utxo_values else 0
        script_type = _determine_script_type(script_pubkey, parsed_sig)
        is_segwit = bool(txin.witness.items)

        if is_segwit:
            if script_type == P2WPKH:
                records.extend(
                    _extract_p2wpkh(tx, vin, script_pubkey, value, txin.witness.items)
                )
            elif script_type == P2WSH:
                records.extend(
                    _extract_p2wsh(tx, vin, script_pubkey, value, txin.witness.items)
                )
            elif script_type == P2SH:
                records.extend(
                    _extract_p2sh_segwit(tx, vin, script_pubkey, value, txin)
                )
        else:
            records.extend(
                _extract_legacy(tx, vin, script_pubkey, parsed_sig)
            )

    return records


def _determine_script_type(script_pubkey: bytes, script_sig: list) -> str:
    if not script_pubkey:
        return "unknown"
    parsed = parse_script(script_pubkey)
    return classify_script_pubkey(parsed)


def _extract_legacy(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    script_sig: list,
) -> list[Record]:
    records: list[Record] = []
    # Reconstruct the script code for P2PKH when script_pubkey is unset
    effective_script = script_pubkey or _guess_p2pkh_script(script_sig)
    # Extract the public key from the scriptSig (last push in P2PKH)
    pubkey_bytes = _extract_pubkey_from_script_sig(script_sig)
    for element in script_sig:
        if isinstance(element, bytes) and len(element) > 1:
            try:
                der = element[:-1]
                flag = element[-1]
                decode_der(der)
                pubkey = _extract_pubkey(tx, vin, der, flag, effective_script, pubkey_bytes)
                records.append(
                    Record(
                        txid=tx.txid(),
                        vin=vin,
                        sig=der,
                        public_key=pubkey,
                        script_type=_determine_script_type(script_pubkey, script_sig),
                        sighash_flag=flag,
                        amount=0,
                    )
                )
            except (ValueError, IndexError):
                continue
    return records


def _guess_p2pkh_script(script_sig: list) -> bytes:
    """Build a P2PKH scriptPubKey from the pubkey in *script_sig*, if present."""
    for element in script_sig:
        if isinstance(element, bytes) and len(element) in {33, 65}:
            from bitcoin.script.builder import make_p2pkh_script
            return make_p2pkh_script(element)
    return b""


def _extract_p2wpkh(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    witness_items: tuple[bytes, ...],
) -> list[Record]:
    records: list[Record] = []
    for item in witness_items[:-1]:
        if len(item) > 1:
            try:
                der = item[:-1]
                flag = item[-1]
                decode_der(der)
                records.append(
                    Record(
                        txid=tx.txid(),
                        vin=vin,
                        sig=der,
                        public_key=_extract_pubkey(tx, vin, der, flag, script_pubkey),
                        script_type=P2WPKH,
                        sighash_flag=flag,
                        amount=value,
                    )
                )
            except (ValueError, IndexError):
                continue
    return records


def _extract_p2wsh(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    witness_items: tuple[bytes, ...],
) -> list[Record]:
    records: list[Record] = []
    for item in witness_items[:-1]:
        if len(item) > 1:
            try:
                der = item[:-1]
                flag = item[-1]
                decode_der(der)
                records.append(
                    Record(
                        txid=tx.txid(),
                        vin=vin,
                        sig=der,
                        public_key=_extract_pubkey(tx, vin, der, flag, script_pubkey),
                        script_type=P2WSH,
                        sighash_flag=item[-1] if item else SIGHASH_ALL,
                        amount=value,
                    )
                )
            except (ValueError, IndexError):
                continue
    return records


def _extract_p2sh_segwit(
    tx: Tx,
    vin: int,
    script_pubkey: bytes,
    value: int,
    txin: "TxIn",
) -> list[Record]:
    records: list[Record] = []
    parsed_sig = parse_script(txin.script_sig)
    if len(parsed_sig) < 2:
        return records
    redeem_script = parsed_sig[-1] if isinstance(parsed_sig[-1], bytes) else b""
    parsed_redeem = parse_script(redeem_script)
    redeem_type = classify_script_pubkey(parsed_redeem)

    witness_items = txin.witness.items
    for item in witness_items[:-1]:
        if len(item) > 1:
            try:
                der = item[:-1]
                flag = item[-1]
                decode_der(der)
                records.append(
                    Record(
                        txid=tx.txid(),
                        vin=vin,
                        sig=der,
                        public_key=_extract_pubkey(tx, vin, der, flag, script_pubkey),
                        script_type=f"p2sh_{redeem_type}",
                        sighash_flag=flag,
                        amount=value,
                    )
                )
            except (ValueError, IndexError):
                continue
    return records


def _extract_pubkey_from_script_sig(script_sig: list) -> bytes | None:
    """Extract the public key from a P2PKH scriptSig (last push)."""
    for element in reversed(script_sig):
        if isinstance(element, bytes) and len(element) in {33, 65}:
            return element
    return None


def _extract_pubkey(
    tx: Tx, vin: int, sig: bytes, flag: int, script: bytes = b"",
    pubkey_bytes: bytes | None = None,
) -> "Point | bytes | None":
    """Recover the public key, falling back to *pubkey_bytes* if recovery fails."""
    message = _compute_sighash(tx, vin, script, flag)
    for rec_id in range(4):
        recovery_flag = 27 + rec_id + 4  # compressed
        try:
            return recover_public_key(message, sig, recovery_flag)
        except ValueError:
            continue
    # Recovery failed; return the scriptSig pubkey if available
    return pubkey_bytes


def _compute_sighash(tx: Tx, vin: int, script: bytes, flag: int) -> bytes:
    from bitcoin.sighash.legacy import sighash_legacy
    from bitcoin.sighash.segwit import sighash_segwit

    if tx.is_segwit():
        # Simplified: assume P2WPKH script code
        script_code = _script_code_for_segwit(tx, vin)
        value = _utxo_value(tx, vin)
        return sighash_segwit(tx, vin, script_code, value, flag)
    return sighash_legacy(tx, vin, script, flag)


def _script_code_for_segwit(tx: Tx, vin: int) -> bytes:
    # Simplified: extract script code from witness program
    return b"\x00" * 22  # placeholder — real implementation would derive from UTXO


def _utxo_value(tx: Tx, vin: int) -> int:
    return 0  # placeholder — caller must provide UTXO data
