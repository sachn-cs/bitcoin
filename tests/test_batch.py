"""Tests for the batch/streaming module.

Note: Old batch tests depended on test_transaction.py which has been removed.
The actual batch API (SignatureStream, BatchProcessor) wraps legacy code.
"""

from __future__ import annotations

from unittest.mock import patch


def test_batch_imports() -> None:
    """Verify batch module imports without errors."""
    import bitcoin.batch
    assert bitcoin.batch.SignatureStream is not None
    assert bitcoin.batch.BatchProcessor is not None
    assert bitcoin.batch.batch_process is not None


def test_batch_process_empty_txids() -> None:
    """Empty txid list returns empty results."""
    from bitcoin.batch import batch_process
    with patch("bitcoin.batch.fetch_transaction"):
        results = batch_process(network="mainnet", timeout=5, mp=False)
    assert results == []
