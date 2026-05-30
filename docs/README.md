# bitcoin — secp256k1 ECDSA Signature Extraction & Linearization

Extract ECDSA signatures (`r`, `s`, `z`) from Bitcoin transactions, derive linear coefficient relations between nonces and private keys, and transform signatures into point-space over secp256k1.

## System Overview

This library parses raw Bitcoin transactions (legacy, SegWit v0, Taproot), extracts ECDSA signatures from all supported script paths, and reconstructs their signature hashes (`z` values). The extracted data feeds a linearization pipeline that derives the scalar relation `d' ≡ αk (mod n)` and the point-space relation `D + βG = αK`.

## Architecture Summary

```
transaction hex → parser.py → Transaction → extractor.py → SignatureCollection
                                                                    │
                                                          linear.py │→ LinearCoefficientCollection
                                                                    │→ LinearPointRelationCollection (via ecc.py)
                                                                    │→ TransformedPointCollection (via ecc.py)
```

The codebase has three layers:

| Layer | Modules | Responsibility |
|-------|---------|----------------|
| **Parsing** | `parser.py`, `script.py`, `der.py`, `utils.py`, `psbt.py` | Transaction bytes → structured models |
| **Extraction** | `extractor.py`, `sighash.py`, `fetcher.py` | Models → signature records with computed `z` |
| **Arithmetic** | `ecc.py`, `linear.py`, `arithmetic.py` | Signatures → linear coefficients → point relations |

Supporting modules: `config.py`, `batch.py`, `serializer.py`, `models.py`, `signature.py`, `coincurve_backend.py`, `ecc_backend.py`, `exceptions.py`.

## Documentation Map

| Document | Content |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Module boundaries, dependency graph, layering |
| [ALGORITHMS.md](ALGORITHMS.md) | DER parsing, sighash, ECC point ops, linearization |
| [MATH.md](MATH.md) | Secp256k1 parameters, ECDSA formulas, linearization math |
| [DATA_FLOW.md](DATA_FLOW.md) | Transaction → signature → coefficient flow |
| [MODULES.md](MODULES.md) | Every module: purpose, dependencies, public API |
| [API.md](API.md) | Public interfaces, commands, SDK surfaces |
| [CONFIGURATION.md](CONFIGURATION.md) | Config files, env vars, defaults |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Direct dependencies and justification |
| [TESTING.md](TESTING.md) | Test strategy, coverage, critical scenarios |
| [GLOSSARY.md](GLOSSARY.md) | Domain terms and acronyms |

## Quick Start

```bash
pip install -e ".[coincurve]"   # optional: C-backed ECC

# Parse and extract signatures
python -m bitcoin.cli extract --tx <hex>

# Derive linear coefficients
python -m bitcoin.cli linear --tx <hex> --input-values 100000,200000

# Transform to point-space
python -m bitcoin.cli transform --tx <hex> --input-values 100000,200000
```

From Python:

```python
from bitcoin.transaction import Transaction

tx = Transaction.parse_hex(hex_str)
tx = tx.with_input_values([100000, 200000])
sig_collection = tx.extract()
linear_coeffs = sig_collection.linear()
point_relations = sig_collection.linear_points()
```

## Development Workflow

```bash
# Install
pip install -e ".[dev,coincurve]"

# Run tests
python -m pytest bitcoin/tests/ -v

# Run benchmarks
python -m pytest bitcoin/tests/ -v --benchmark-only
```

## Key Terms

See [GLOSSARY.md](GLOSSARY.md) for a full list of domain terms, acronyms, and internal terminology.

## What Is Not Documented

- **Operations / Deployment**: This is a library and CLI tool. No server deployment, migrations, or operational runbooks exist.
- **Security**: No authentication, authorization, secrets management, or trust boundaries exist in this codebase. The library does not connect to user wallets or handle private keys.
- **Performance**: Benchmarks exist in `test_benchmarks.py` but no formal performance architecture is defined.
- **Decision Records**: No ADRs exist. Architectural rationale is captured inline in docstrings and this documentation.
