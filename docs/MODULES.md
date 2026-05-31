# Modules

## `bitcoin.field` — Modular Arithmetic

**Submodules**: `modular.py`, `sqrt.py`

**Dependencies**: None (stdlib)

**Public API** (re-exported via `bitcoin.field`):
| Symbol | Kind | Description |
|--------|------|-------------|
| `inverse` | Function | Extended Euclidean modular inverse |
| `sqrt` | Function | Tonelli-Shanks sqrt (p ≡ 3 mod 4 specialization) |
| `pow_mod` | Function | Modular exponentiation |
| `validate_non_negative` | Function | Assert value is non-negative int |

**Consumers**: `bitcoin.curve`, `bitcoin.signature`

---

## `bitcoin.curve` — ECC Point Operations

**Submodules**: `point.py`, `operations.py`, `params.py`, `backend.py`, `native_backend.py`, `libsecp_backend.py`, `dispatch.py`

**Dependencies**: `field`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `Point` | Class | Frozen affine point with SEC serialization methods |
| `GENERATOR` | Constant | Secp256k1 generator point |
| `INFINITY` | Constant | Identity element |
| `CURVE_ORDER` | Constant | Curve order n |
| `FIELD_PRIME` | Constant | Field prime p |
| `CurveBackend` | ABC | Abstract backend interface |
| `NativeBackend` | Class | Pure Python backend |
| `LibsecpBackend` | Class | Coincurve-backed backend |
| `set_backend` / `get_backend` | Functions | Backend dispatch |
| `negate`, `add`, `double`, `multiply` | Functions | Point operations |
| `is_on_curve` | Function | Curve membership test |
| `sqrt_field` | Function | Field sqrt for y recovery |
| `parse_public_key` / `serialize_public_key` | Functions | SEC key I/O |
| `normalize` / `normalize_non_negative` | Functions | Scalar helpers |

**Consumers**: `encoding`, `signature`

---

## `bitcoin.encoding` — Binary Encoding

**Submodules**: `hex.py`, `binary.py`, `varint.py`, `der.py`, `sec.py`, `hasher.py`

**Dependencies**: None (stdlib)

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `encode_hex` / `decode_hex` | Functions | Hex I/O |
| `encode_varint` / `decode_varint` | Functions | Bitcoin varint |
| `encode_der` / `decode_der` | Functions | Strict BIP-66 DER |
| `parse_sec` / `serialize_sec` | Functions | SEC public key |
| `sha256`, `hash256`, `hash160` | Functions | Hashing |
| `tagged_hash` | Function | BIP-340 tagged hash |
| `bytes_to_int` / `int_to_bytes` | Functions | Integer conversion |
| `read_exactly` | Function | Bounded binary read |

**Consumers**: All packages (encoding, script, transaction, sighash, signature, etc.)

---

## `bitcoin.script` — Bitcoin Script

**Submodules**: `opcodes.py`, `parser.py`, `classifier.py`, `builder.py`

**Dependencies**: `encoding` (opcode values), `exceptions`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `parse_script` | Function | Bytes → script element list |
| `serialize_script` | Function | Elements → bytes |
| `classify_script_pubkey` | Function | Output script → type constant |
| `classify_script_sig` | Function | Input script → type constant |
| `ScriptChunk` | Dataclass | Parsed script element |
| `build_p2pkh`, `build_p2wpkh`, etc. | Functions | Script construction |
| `P2PK`, `P2PKH`, `P2SH`, `P2WPKH`, `P2WSH`, `P2TR` | Constants | Script type identifiers |
| Opcode constants | Constants | `OP_DUP`, `OP_HASH160`, etc. |

**Consumers**: `transaction`, `sighash`, `signature`

---

## `bitcoin.transaction` — Transaction Models

**Submodules**: `models.py`, `parser.py`, `tx.py`

**Dependencies**: `encoding`, `exceptions`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `Tx` | Class | Frozen transaction with `txid()`, `is_segwit()` |
| `TxIn` | Class | Transaction input |
| `TxOut` | Class | Transaction output |
| `OutPoint` | Class | Previous output reference |
| `Witness` | Class | Witness stack |
| `parse_tx` | Function | Raw bytes → `(Tx, bytes_consumed)` |
| `make_tx` | Function | Convenience tx builder |

**Consumers**: `sighash`, `signature`, `psbt`, `cli`

---

## `bitcoin.sighash` — Sighash Computation

**Submodules**: `flag.py`, `legacy.py`, `segwit.py`, `taproot.py`

**Dependencies**: `encoding`, `transaction`, `script`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `sighash_legacy` | Function | Pre-SegWit hash |
| `sighash_segwit` | Function | BIP-143 SegWit v0 hash |
| `sighash_taproot` | Function | BIP-341 Taproot hash |
| `SIGHASH_ALL`, `SIGHASH_NONE`, etc. | Constants | Sighash flag values |
| `require_sighash_flag` | Function | Validate flag byte |

**Consumers**: `signature`

---

## `bitcoin.signature` — Signature Type, Extraction & Linearization

**Submodules**: `record.py`, `collection.py`, `check.py`, `extraction/engine.py`, `linearization/engine.py`

**Dependencies**: `curve`, `encoding`, `transaction`, `sighash`, `exceptions`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `Record` | Class | Frozen extraction result: `txid`, `vin`, `sig`, `public_key`, `script_type`, `sighash_flag`, `amount` |
| `SignatureCollection` | Class | Collection of records with shared state |
| `extract_signatures` | Function | `Tx` → `list[Record]` |
| `linearize_signatures` | Function | `list[Record]` → sorted `list[Record]` |
| `verify_sig` | Function | Verify ECDSA signature |
| `recover_public_key` | Function | Recover pubkey from message + signature |

**Consumers**: `psbt`, `cli`

---

## `bitcoin.psbt` — PSBT Parsing

**Submodules**: `models.py`, `parser.py`

**Dependencies**: `transaction`, `encoding`, `signature`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `Psbt` | Class | Frozen PSBT with unsigned tx, input/output maps |
| `PsbtInput` / `PsbtOutput` | Classes | Per-input/output PSBT data |
| `parse_psbt` | Function | Raw bytes → `Psbt` |
| `serialize_psbt` | Function | `Psbt` → raw bytes |
| `parse_psbt_hex` | Function | Hex string → `Psbt` |

**Consumers**: `cli`, scripts

---

## `bitcoin.services` — Serialization

**Submodules**: `serializer.py`

**Dependencies**: `transaction`, `encoding`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `serialize_tx` | Function | `Tx` → raw bytes |
| `serialize_legacy_tx` | Function | `Tx` → legacy format bytes |

---

## `bitcoin.cli` — CLI

**Submodules**: `app.py`

**Dependencies**: `typer`, `signature`, `encoding`, `transaction`

**Commands**:
| Command | Description |
|---------|-------------|
| `extract` | Parse tx hex, extract signatures |
| `linearize` | Extract + sort by txid/vin |
| `version` | Print version |

**Entry point**: `main(args) → int` (0 success, 1 error, 2 usage)

---

## `bitcoin.exceptions` — Exception Types

**Dependencies**: None

| Exception | Parent | Raised When |
|-----------|--------|-------------|
| `BitcoinError` | `Exception` | Base for all package errors |
| `NotInvertible` | `BitcoinError` | Value has no modular inverse |
| `PointError` | `BitcoinError` | Invalid curve point |
| `InvalidSignature` | `BitcoinError` | Signature validation fails |
| `InvalidDerSignature` | `BitcoinError` | DER format violation |
| `ParsingError` | `BitcoinError` | Transaction/script parse failure |

---

## `bitcoin.settings` — Global Settings

**Dependencies**: None

| Feature | Description |
|---------|-------------|
| `settings.strict_mode` | If True, raise on non-fatal issues |
| `settings.default_backend` | Backend name (`"native"`, `"libsecp"`, or `None`) |
| `settings.max_extraction_inputs` | Cap on inputs processed during extraction |
