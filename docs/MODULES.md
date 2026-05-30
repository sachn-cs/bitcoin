# Modules

## `bitcoin.arithmetic` — Modular Arithmetic

**File**: `bitcoin/arithmetic.py`

**Purpose**: Pure arithmetic logic (modular inversion, non-negative validation) without domain-specific error types. Each consuming module wraps these with its own exception hierarchy.

**Dependencies**: None (stdlib only)

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `NotInvertibleError` | Exception | Value has no modular inverse (subclass of `ValueError`) |
| `normalize_non_negative` | Function | Validate value is a non-negative int |
| `inverse_mod` | Function | Extended Euclidean algorithm modular inverse |

**Consumers**: `ecc.py`, `linear.py`

---

## `bitcoin.batch` — Batch Processing

**File**: `bitcoin/batch.py`

**Purpose**: Sequential and parallel processing of multiple transactions. Provides `BatchProcessor` for programmatic use and `batch_process()` as a convenience function.

**Dependencies**: `exceptions`, `extractor`, `fetcher`, `models`, `signature`, `transaction`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `BatchProcessor` | Class | Configured fetcher+extractor for batch txid processing |
| `SignatureStream` | Class | Lazy stream over signature records with filter/map |
| `batch_process` | Function | Convenience: one or more txids, optional multiprocessing |

**Consumers**: CLI (not directly — used by scripts and programmatic callers)

---

## `bitcoin.cli` — Command-Line Interface

**File**: `bitcoin/cli.py`

**Purpose**: Typer-based CLI for parsing, extraction, linearization, point derivation, and transformation.

**Dependencies**: `click`, `typer`, `exceptions`, `serializer`, `transaction`

**Commands**:
| Command | Description |
|---------|-------------|
| `parse` | Parse and display transaction structure |
| `extract` | Extract r, s, z values from signatures |
| `linear` | Derive linear coefficients α, β |
| `points` | Derive point-space relations D + βG = αK |
| `transform` | Transform signatures to D' = d'G point-space |

**Entry point**: `main(args)` — returns exit code (0 success, 1 error, 2 usage)

---

## `bitcoin.coincurve_backend` — Coincurve ECC Backend

**File**: `bitcoin/coincurve_backend.py`

**Purpose**: ECC backend implementation wrapping `coincurve` (libsecp256k1 C bindings).

**Dependencies**: `ecc_backend`, `ecc` (runtime imports)

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `CoincurveBackend` | Class | Implements all `EccBackend` abstract methods |

**Fallback behavior**: `point_negate`, `point_add`, `point_double` fall back to pure Python because coincurve does not expose those raw operations. Logged at DEBUG on initialization.

---

## `bitcoin.config` — Configuration System

**File**: `bitcoin/config.py`

**Purpose**: Environment-variable and config-file overrides for package settings.

**Dependencies**: `os`, `pathlib`, `json` (lazy), `dataclasses`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `Config` | Dataclass | Configuration with env-var and file loading |

**Settings**:
| Field | Env Var | Default | Type |
|-------|---------|---------|------|
| `ecc_backend` | `BITCOIN_ECC_BACKEND` | `"python"` | str |
| `network` | `BITCOIN_NETWORK` | `"mainnet"` | str |
| `fetch_timeout` | `BITCOIN_FETCH_TIMEOUT` | `30` | int |
| `strict_parsing` | `BITCOIN_STRICT_PARSING` | `True` | bool |

---

## `bitcoin.der` — DER Signature Parsing

**File**: `bitcoin/der.py`

**Purpose**: Strict DER-encoded ECDSA signature parsing with trailing sighash byte.

**Dependencies**: `exceptions`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `ParsedSignature` | Dataclass | Parsed `r`, `s` bytes and `sighash_flag` |
| `parse_der_signature` | Function | DER → `ParsedSignature` |

**Consumers**: `extractor.py`, `psbt.py`

---

## `bitcoin.ecc` — ECC Point Arithmetic

**File**: `bitcoin/ecc.py`

**Purpose**: Secp256k1 affine point operations, SEC encoding, public API for the ECC backend dispatch system.

**Dependencies**: `arithmetic`, `ecc_backend`, `exceptions`, `linear`, `models`, `utils`

**Public API (via `__all__`)**:
- Curve constants: `SECP256K1_FIELD_PRIME`, `SECP256K1_ORDER`, `SECP256K1_A`, `SECP256K1_B`, `G`, `SECP256K1_INFINITY`
- Types: `Secp256k1Point`, `LinearPointRelation`, `LinearPointRelationCollection`, `TransformedPointRecord`, `TransformedPointCollection`
- Point ops: `point_negate`, `point_add`, `point_double`, `scalar_multiply`, `is_on_curve`, `field_sqrt`
- Encoding: `parse_sec_public_key`, `serialize_sec_public_key`, plus `*_py` variants
- Derivation: `derive_point_relation`, `derive_transformed_point`
- Arithmetic: `inverse_mod`, `normalize_non_negative`, `normalize_field_element`
- Exceptions: `InvalidSecp256k1PointError`, `InvalidSecPublicKeyError`
- Helpers: `int_to_bytes`

**Consumers**: `signature.py`, `coincurve_backend.py`, `__init__.py`, tests

---

## `bitcoin.ecc_backend` — ECC Backend Interface

**File**: `bitcoin/ecc_backend.py`

**Purpose**: Abstract base class for pluggable ECC backends and global backend state.

**Dependencies**: `ecc` (TYPE_CHECKING only)

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `EccBackend` | ABC | Abstract interface with 9 methods |
| `get_backend` | Function | Return current backend or None |
| `set_backend` | Function | Set backend (validates type) |

**Consumers**: `ecc.py`, `coincurve_backend.py`, `__init__.py`

---

## `bitcoin.exceptions` — Exception Types

**File**: `bitcoin/exceptions.py`

**Dependencies**: None

**Public API**:
| Exception | Parent | Raised When |
|-----------|--------|-------------|
| `BitcoinError` | `Exception` | Base for all package errors |
| `InvalidHexError` | `BitcoinError` | Hex string malformed |
| `TruncatedTransactionError` | `BitcoinError` | Transaction bytes end unexpectedly |
| `MalformedVarintError` | `BitcoinError` | Compact size integer invalid |
| `UnsupportedTransactionError` | `BitcoinError` | Transaction uses unsupported structure |
| `UnsupportedScriptPathError` | `BitcoinError` | Unsupported script path |
| `InvalidDerSignatureError` | `BitcoinError` | DER signature rules violated |
| `InvalidSighashFlagError` | `BitcoinError` | Sighash flag bits unsupported |
| `MissingInputValueError` | `BitcoinError` | SegWit value needed but unavailable |
| `ScriptParseError` | `BitcoinError` | Script cannot be parsed |
| `LinearCoefficientError` | `BitcoinError` | Linear coefficient derivation fails |
| `InvalidLinearCoefficientError` | `LinearCoefficientError` | Signature value invalid for linearization |
| `NonInvertibleLinearCoefficientError` | `LinearCoefficientError` | Coefficient has no modular inverse |
| `InvalidSecp256k1PointError` | `BitcoinError` | Point or SEC encoding is invalid |
| `InvalidSecPublicKeyError` | `InvalidSecp256k1PointError` | SEC key parsing or serialization fails |

---

## `bitcoin.extractor` — Signature Extraction

**File**: `bitcoin/extractor.py`

**Purpose**: Dispatch script types and build signature records from parsed transactions.

**Dependencies**: `der`, `exceptions`, `models`, `script`, `sighash`, `signature`, `utils`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `extract_signatures` | Function | Extract all signatures from a transaction |

**Internals (private)**: `_extract_input_signatures`, `_build_records`, `_extract_legacy_p2pkh`, `_extract_legacy_p2sh_multisig`, `_extract_native_p2wpkh`, `_extract_p2sh_p2wpkh`, `_extract_native_p2wsh_multisig`, `_extract_p2sh_p2wsh_multisig`, `_extract_taproot_key_path`, `_extract_taproot_script_path`, `_resolve_input_value`

---

## `bitcoin.fetcher` — Transaction Fetching

**File**: `bitcoin/fetcher.py`

**Purpose**: Fetch Bitcoin transactions and address data from the blockstream.info API.

**Dependencies**: `exceptions`, `signature`, `transaction`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `fetch_transaction_hex` | Function | Fetch raw tx hex by txid |
| `fetch_transaction` | Function | Fetch and parse a transaction |
| `fetch_address_transactions` | Function | Fetch recent txs for an address |
| `fetch_address_utxos` | Function | Fetch UTXOs for an address |
| `fetch_and_extract` | Function | Fetch + attach values + extract |

---

## `bitcoin.linear` — Linear Coefficient Derivation

**File**: `bitcoin/linear.py`

**Purpose**: Derive α and β coefficients from extracted ECDSA signature data.

**Dependencies**: `arithmetic`, `exceptions`, `models`, `utils`

**Public API (via `__all__`)**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `LinearCoefficientRecord` | Dataclass | One linearized signature relation |
| `LinearCoefficientCollection` | Dataclass | Immutable collection |
| `derive_linear_coefficients` | Function | `SignatureRecord` → `LinearCoefficientRecord` |
| `inverse_mod` | Function | Modular inverse with domain error wrapping |
| `normalize_non_negative` | Function | Non-negative int validation |
| `NotInvertibleError` | Exception | Re-exported from `arithmetic` |
| `SECP256K1_ORDER` | Constant | Curve order |

---

## `bitcoin.models` — Data Models

**File**: `bitcoin/models.py`

**Purpose**: Pure data carriers with no behavior.

**Dependencies**: None

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `TransactionInput` | Dataclass | Parsed tx input (prevout, script_sig, witness) |
| `TransactionOutput` | Dataclass | Parsed tx output (value, script_pubkey) |
| `TransactionContext` | Dataclass | Input values for SegWit sighash |
| `SignatureRecord` | Dataclass | Extracted r, s, z, metadata |

---

## `bitcoin.parser` — Transaction Parsing

**File**: `bitcoin/parser.py`

**Purpose**: Parse raw Bitcoin transaction bytes into structured models.

**Dependencies**: `exceptions`, `models`, `utils`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `ParsedTransaction` | Dataclass | Parsed transaction fields |
| `parse_transaction_bytes` | Function | Raw bytes → `ParsedTransaction` |

---

## `bitcoin.psbt` — PSBT Parsing & Extraction

**File**: `bitcoin/psbt.py`

**Purpose**: BIP-174 PSBT parsing and signature extraction from `partial_sigs` fields.

**Dependencies**: `der`, `exceptions`, `models`, `parser`, `script`, `sighash`, `signature`, `transaction`, `utils`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `PsbtInput` | Dataclass | Per-input PSBT key-value data |
| `PsbtOutput` | Dataclass | Per-output PSBT key-value data |
| `Psbt` | Dataclass | Parsed PSBT |
| `parse_psbt` | Function | Raw bytes → `Psbt` |
| `parse_psbt_hex` | Function | Hex string → `Psbt` |
| `psbt_extract_signatures` | Function | `Psbt` → `SignatureCollection` |

---

## `bitcoin.script` — Bitcoin Script

**File**: `bitcoin/script.py`

**Purpose**: Script parsing into chunks, push-data extraction, script-type classification.

**Dependencies**: `exceptions`, `utils`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `ScriptChunk` | Dataclass | One parsed script item |
| `parse_script` | Function | Bytes → `tuple[ScriptChunk, ...]` |
| `chunks_to_pushes` | Function | Filter to push-data items |
| `remove_code_separators` | Function | Verify no OP_CODESEPARATOR |
| `is_p2pkh_pushes` | Function | P2PKH pattern check |
| `is_witness_program` | Function | SegWit program check |
| `witness_program_hash_size` | Function | Hash size of witness program |
| `is_taproot` | Function | Taproot output check |
| `is_taproot_script_path` | Function | Taproot script-path check |
| `make_p2pkh_script` | Function | Build P2PKH scriptPubKey |
| `parse_multisig_redeem_script` | Function | Parse multisig → (m, pubkeys) |

---

## `bitcoin.serializer` — JSON Serialization

**File**: `bitcoin/serializer.py`

**Purpose**: Centralized I/O formatting for all domain types.

**Dependencies**: `utils`, `ecc`/`linear`/`signature`/`transaction` (TYPE_CHECKING only)

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `point_to_dict`/`_json` | Functions | `Secp256k1Point` → dict/JSON |
| `linear_record_to_dict` | Function | `LinearCoefficientRecord` → dict |
| `linear_collection_to_dict`/`_json` | Functions | Collection → dict/JSON |
| `point_relation_to_dict` | Function | `LinearPointRelation` → dict |
| `point_relation_collection_to_dict`/`_json` | Functions | Collection → dict/JSON |
| `transformed_point_record_to_dict` | Function | `TransformedPointRecord` → dict |
| `transformed_point_collection_to_dict` | Function | Collection → dict |
| `signature_collection_to_dict`/`_json` | Functions | Collection → dict/JSON |
| `transaction_to_dict`/`_json` | Functions | `Transaction` → dict/JSON |
| `to_json_string`/`to_pretty_json_string` | Functions | Low-level JSON formatting |
| `to_hex`/`int_to_hex_0x` | Functions | Value → hex string helpers |

---

## `bitcoin.signature` — Signature Collection

**File**: `bitcoin/signature.py`

**Purpose**: `SignatureCollection` dataclass with derived operations (linear, transform, point-space).

**Dependencies**: `ecc`, `exceptions`, `linear`, `models`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `SignatureCollection` | Dataclass | Immutable collection with `.linear()`, `.linear_points()`, `.transform_points()` |

---

## `bitcoin.transaction` — Transaction Model

**File**: `bitcoin/transaction.py`

**Purpose**: `Transaction` dataclass with `parse_hex`, `with_input_values`, and `extract` methods.

**Dependencies**: `extractor`, `models`, `parser`, `signature`, `utils`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `Transaction` | Dataclass | Transaction with parsing and extraction |

---

## `bitcoin.utils` — Utilities

**File**: `bitcoin/utils.py`

**Purpose**: Hex validation, serialization, hashing, and `ByteReader` for bounded binary reads.

**Dependencies**: `exceptions`

**Public API**:
| Symbol | Kind | Description |
|--------|------|-------------|
| `validate_hex_string` | Function | Hex → bytes with validation |
| `bytes_to_hex` | Function | Bytes → lowercase hex |
| `int_to_hex` | Function | Non-negative int → hex string |
| `little_endian_bytes_to_int` | Function | LE bytes → int |
| `int_to_little_endian_bytes` | Function | Non-negative int → LE bytes |
| `sha256d` | Function | Double-SHA256 |
| `hash160` | Function | SHA256 + RIPEMD160 |
| `ByteReader` | Class | Bounded binary reader with typed reads |

---

## `bitcoin.__init__` — Package Exports

**File**: `bitcoin/__init__.py`

**Purpose**: Public package interface. Re-exports all user-facing symbols from submodules.
