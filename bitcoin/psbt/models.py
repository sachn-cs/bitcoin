"""PSBT (Partially Signed Bitcoin Transaction) data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass(frozen=True, slots=True)
class PsbtInput:
    """A PSBT input map."""

    non_witness_utxo: Optional[bytes] = None
    witness_utxo: Optional[bytes] = None
    partial_sigs: Dict[bytes, bytes] = field(default_factory=dict)
    sighash_type: Optional[int] = None
    redeem_script: Optional[bytes] = None
    witness_script: Optional[bytes] = None
    bip32_derivations: Dict[bytes, bytes] = field(default_factory=dict)
    final_script_sig: Optional[bytes] = None
    final_script_witness: Optional[Tuple[bytes, ...]] = None
    proprietary: Dict[bytes, bytes] = field(default_factory=dict)
    unknown: Dict[bytes, bytes] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PsbtOutput:
    """A PSBT output map."""

    redeem_script: Optional[bytes] = None
    witness_script: Optional[bytes] = None
    bip32_derivations: Dict[bytes, bytes] = field(default_factory=dict)
    proprietary: Dict[bytes, bytes] = field(default_factory=dict)
    unknown: Dict[bytes, bytes] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Psbt:
    """A Partially Signed Bitcoin Transaction."""

    tx: bytes  # raw unsigned transaction
    inputs: Tuple[PsbtInput, ...]
    outputs: Tuple[PsbtOutput, ...]
    unknown: Dict[bytes, bytes] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if len(self.inputs) != len(self.outputs):
            raise ValueError(
                f"Mismatched input/output count in PSBT: "
                f"{len(self.inputs)} inputs vs {len(self.outputs)} outputs."
            )
