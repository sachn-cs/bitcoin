# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Top-level linearization API — re-exports ``linearize_signatures``."""

from bitcoin.signature.linearization.engine import linearize_signatures

__all__ = [
    "linearize_signatures",
]
