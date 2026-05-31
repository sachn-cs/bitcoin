"""ECDSA signature types, extraction, and linearization.

New API.
"""

from bitcoin.signature.record import Record
from bitcoin.signature.collection import SignatureCollection
from bitcoin.signature.check import recover_public_key, verify_sig
from bitcoin.signature.extraction import extract_signatures
from bitcoin.signature.linearization import linearize_signatures

__all__ = [
    "Record",
    "SignatureCollection",
    "extract_signatures",
    "linearize_signatures",
    "recover_public_key",
    "verify_sig",
]
