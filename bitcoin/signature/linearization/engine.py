"""Signature linearization engine — sort extracted signatures."""

from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from bitcoin.signature.record import Record


def linearize_signatures(records: list[Record]) -> list[Record]:
    """Sort extracted signatures by (txid, vin) for deterministic ordering.

    The linearization produces a canonical, reproducible order that is
    suitable for serialization, comparison, and threshold-based analysis.

    Arguments:
        records: A list of ``Record`` instances.

    Returns:
        A new list sorted by ``(txid, vin)``.
    """
    return sorted(records, key=_record_sort_key)


def _record_sort_key(record: Record) -> tuple[bytes, int]:
    return (record.txid, record.vin)
