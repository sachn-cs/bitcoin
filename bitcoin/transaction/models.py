"""Transaction data models (TxIn, TxOut, Tx, Witness)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True, slots=True)
class OutPoint:
    """Reference to a previous transaction output."""

    txid: bytes  # 32 bytes, little-endian
    vout: int  # output index

    def __post_init__(self) -> None:
        if len(self.txid) != 32:
            raise ValueError(f"txid must be 32 bytes, got {len(self.txid)}.")
        if self.vout < 0:
            raise ValueError(f"vout must be non-negative, got {self.vout}.")


@dataclass(frozen=True, slots=True)
class TxIn:
    """A transaction input."""

    previous_output: OutPoint
    script_sig: bytes
    sequence: int
    witness: Witness

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError(f"Sequence must be non-negative, got {self.sequence}.")


@dataclass(frozen=True, slots=True)
class TxOut:
    """A transaction output."""

    value: int  # satoshis
    script_pubkey: bytes

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError(f"Value must be non-negative, got {self.value}.")
        # 21 million BTC max
        if self.value > 21_000_000 * 100_000_000:
            raise ValueError(f"Value exceeds maximum: {self.value}.")


@dataclass(frozen=True, slots=True)
class Witness:
    """A SegWit witness stack."""

    items: tuple[bytes, ...]

    def __init__(self, items: tuple[bytes, ...] = ()) -> None:
        object.__setattr__(self, "items", items)

    def __len__(self) -> int:
        return len(self.items)


EMPTY_WITNESS = Witness(())


@dataclass(frozen=True, slots=True)
class Tx:
    """A Bitcoin transaction."""

    version: int
    inputs: tuple[TxIn, ...]
    outputs: tuple[TxOut, ...]
    lock_time: int

    def is_segwit(self) -> bool:
        """Return True if any input has a non-empty witness."""
        return any(txin.witness.items for txin in self.inputs)

    def txid(self) -> bytes:
        """Return the transaction ID (hash of legacy serialization).

        This is computed at import time to avoid pulling in hasher just for
        the property.  See ``services.serializer``.
        """
        from bitcoin.encoding.hasher import hash256
        from bitcoin.services.serializer import serialize_legacy_tx

        return hash256(serialize_legacy_tx(self))

    def wtxid(self) -> bytes:
        """Return the witness txid (hash of full serialization)."""
        from bitcoin.encoding.hasher import hash256
        from bitcoin.services.serializer import serialize_tx

        return hash256(serialize_tx(self))
