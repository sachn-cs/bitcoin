"""Test helpers for constructing transactions."""
from __future__ import annotations

from bitcoin.transaction import Tx, TxIn, TxOut, OutPoint, Witness, make_tx


def make_p2pkh_transaction() -> tuple[str, bytes, bytes]:
    """Build a minimal P2PKH transaction with dummy values.

    Returns:
        (hex_string, txid, script_pubkey)
    """
    tx = make_tx(
        version=2,
        inputs=[
            {
                "txid": b"\x00" * 31 + b"\x01",
                "vout": 0,
            }
        ],
        outputs=[
            {"value": 10000, "script_pubkey": b"\x76\xa9\x14" + b"\x00" * 20 + b"\x88\xac"}
        ],
    )
    from bitcoin.services.serializer import serialize_tx
    raw = serialize_tx(tx)
    return raw.hex(), tx.txid(), b"\x76\xa9\x14" + b"\x00" * 20 + b"\x88\xac"
