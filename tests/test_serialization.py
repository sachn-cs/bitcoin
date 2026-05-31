"""Tests for transaction serialization."""
from __future__ import annotations

import pytest

from bitcoin import Tx, TxIn, TxOut, OutPoint, Witness, parse_tx
from bitcoin.services.serializer import serialize_tx, serialize_legacy_tx
from bitcoin.encoding import decode_hex, encode_varint


class TestSerializeTx:
    def test_serialize_legacy_empty(self) -> None:
        """Empty legacy transaction serializes correctly."""
        tx = Tx(version=1, inputs=(), outputs=(), lock_time=0)
        raw = serialize_tx(tx)
        # version(4) + inputs_varint(1) + outputs_varint(1) + locktime(4) = 10 bytes
        assert len(raw) == 10

    def test_serialize_roundtrip_empty(self) -> None:
        """Serialize then parse gives back the same tx."""
        tx = Tx(version=2, inputs=(), outputs=(), lock_time=100)
        raw = serialize_tx(tx)
        parsed, _ = parse_tx(raw)
        assert parsed.version == 2
        assert parsed.lock_time == 100

    def test_serialize_legacy_tx(self) -> None:
        """serialize_legacy_tx produces legacy format (no witness)."""
        tx = Tx(version=1, inputs=(), outputs=(), lock_time=0)
        raw = serialize_legacy_tx(tx)
        assert len(raw) == 10

    def test_serialize_segwit_tx(self) -> None:
        """SegWit tx has different serialization from legacy."""
        txin = TxIn(
            OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness((b"\x30\x45",)),
        )
        tx = Tx(version=2, inputs=(txin,), outputs=(), lock_time=0)
        raw = serialize_tx(tx)
        assert raw[4] == 0x00  # segwit marker
        assert len(raw) > 10

    def test_serialize_varint_0(self) -> None:
        assert encode_varint(0) == b"\x00"

    def test_serialize_varint_252(self) -> None:
        assert encode_varint(0xFC) == b"\xfc"

    def test_serialize_varint_253(self) -> None:
        encoded = encode_varint(0xFD)
        assert encoded[0] == 0xFD
        assert len(encoded) == 3

    def test_serialize_varint_large(self) -> None:
        encoded = encode_varint(0x10000)
        assert encoded[0] == 0xFE
        assert len(encoded) == 5

    def test_serialize_varint_huge(self) -> None:
        encoded = encode_varint(0x100000000)
        assert encoded[0] == 0xFF
        assert len(encoded) == 9

    def test_serialize_txid_consistency(self) -> None:
        """txid remains the same after serialize-then-parse (legacy serialization)."""
        tx = Tx(version=1, inputs=(), outputs=(), lock_time=0)
        orig_id = tx.txid()
        raw = serialize_tx(tx)
        parsed, _ = parse_tx(raw)
        assert parsed.txid() == orig_id

    def test_serialize_tx_txid_segwit(self) -> None:
        """txid for segwit tx uses legacy-hash (no witness)."""
        txin = TxIn(
            OutPoint(txid=b"\x00" * 32, vout=0),
            script_sig=b"",
            sequence=0xFFFFFFFF,
            witness=Witness((b"\x30\x45",)),
        )
        tx = Tx(version=2, inputs=(txin,), outputs=(), lock_time=0)
        segwit_raw = serialize_tx(tx)
        legacy_raw = serialize_legacy_tx(tx)
        assert segwit_raw != legacy_raw
        assert tx.txid() == parse_tx(legacy_raw)[0].txid()
