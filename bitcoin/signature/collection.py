"""Collection of extracted signature records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, TYPE_CHECKING

from bitcoin.signature.record import Record

if TYPE_CHECKING:
    from bitcoin.linear import LinearCoefficientCollection


@dataclass(frozen=True, slots=True)
class SignatureCollection:
    """An immutable collection of ``Record`` instances."""

    records: tuple[Record, ...]

    def __init__(self, records: Sequence[Record] = ()) -> None:
        object.__setattr__(self, "records", tuple(records))

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def __getitem__(self, index):
        return self.records[index]

    def linear(self) -> object:
        """Derive linear coefficients for each record.

        Returns:
            A ``LinearCoefficientCollection``.
        """
        from bitcoin.linear import derive_linear_coefficients, LinearCoefficientCollection
        records_tuple = tuple(
            derive_linear_coefficients(r) for r in self.records
        )
        return LinearCoefficientCollection(records=records_tuple)
