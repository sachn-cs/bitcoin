# Copyright (c) 2026 secp contributors
# SPDX-License-Identifier: MIT
"""Top-level extraction API — re-exports ``extract_signatures``."""

from bitcoin.signature.extraction.engine import extract_signatures

__all__ = [
    "extract_signatures",
]
