"""Transaction construction utilities."""

from __future__ import annotations

from typing import List, Sequence

from bitcoin.transaction.models import Tx, TxIn, TxOut, OutPoint, Witness, EMPTY_WITNESS


def make_tx(
    version: int,
    inputs: Sequence[dict],
    outputs: Sequence[dict],
    lock_time: int = 0,
) -> Tx:
    """Build a ``Tx`` from dictionaries (for convenience).

    Each *inputs* entry::

        {"txid": bytes, "vout": int, "script_sig": bytes,
         "sequence": int, "witness": tuple[bytes, ...]}

    Each *outputs* entry::

        {"value": int, "script_pubkey": bytes}
    """
    txins: list[TxIn] = []
    for inp in inputs:
        witness = Witness(tuple(inp.get("witness", ())))
        txins.append(
            TxIn(
                previous_output=OutPoint(txid=inp["txid"], vout=inp["vout"]),
                script_sig=inp.get("script_sig", b""),
                sequence=inp.get("sequence", 0xFFFFFFFF),
                witness=witness,
            )
        )
    txouts = [TxOut(value=out["value"], script_pubkey=out["script_pubkey"]) for out in outputs]
    return Tx(version=version, inputs=tuple(txins), outputs=tuple(txouts), lock_time=lock_time)
