"""Bitcoin transaction types and parsing.

New API.
"""

from bitcoin.transaction.models import OutPoint, TxIn, TxOut, Tx, Witness, EMPTY_WITNESS
from bitcoin.transaction.parser import parse_tx
from bitcoin.transaction.tx import make_tx

__all__ = [
    "EMPTY_WITNESS",
    "OutPoint",
    "Tx",
    "TxIn",
    "TxOut",
    "Witness",
    "make_tx",
    "parse_tx",
]
