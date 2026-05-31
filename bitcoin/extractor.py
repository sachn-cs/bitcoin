"""Legacy signature extraction — delegates to the new API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bitcoin.signature import SignatureCollection
from bitcoin.exceptions import MissingInputValueError
from bitcoin.models import TransactionContext

if TYPE_CHECKING:
    pass

__all__ = [
    "extract_signatures",
    "resolve_input_value",
]


def extract_signatures(
    tx: object,
    utxo_script_pubkeys: list[bytes] | None = None,
    utxo_values: list[int] | None = None,
) -> SignatureCollection:
    """Extract signatures using the new ``signature.extraction`` engine."""
    from bitcoin.signature.extraction.engine import extract_signatures as _extract
    records = _extract(tx, utxo_script_pubkeys, utxo_values)
    return SignatureCollection(records=tuple(records))


def resolve_input_value(context: TransactionContext | None,
                        input_index: int) -> int | None:
    """Return the spent output value for an input from the transaction context."""
    if context is None:
        return None
    if input_index >= len(context.input_values):
        raise MissingInputValueError(
            f"Input index {input_index} exceeds context "
            f"({len(context.input_values)} values available).")
    return context.input_values[input_index]
