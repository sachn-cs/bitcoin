# secp — secp256k1 ECDSA Signature Extraction & Analysis

Extract ECDSA signatures (r, s, z) from Bitcoin transactions, recover public keys, verify signatures, and derive linear relations between nonces and private keys over secp256k1.

## Architecture

```
field  →  curve  →  encoding  →  script  →  transaction  →  sighash  →  signature  →  psbt  →  services  →  cli
```

10 packages with strict one-way dependency. No circular imports.

| Package | Responsibility |
|---------|----------------|
| `field` | Modular arithmetic, square roots |
| `curve` | Point operations, backends (native, libsecp) |
| `encoding` | DER, SEC, varint, hex, hashing |
| `script` | Script parsing, classification, building |
| `transaction` | Tx models, parsing, construction |
| `sighash` | Legacy, SegWit, Taproot sighash computation |
| `signature` | Record, extraction engine, verification, linearization |
| `psbt` | PSBT parsing and writing |
| `services` | Serialization, blockchain fetching |
| `cli` | Typer CLI: `extract`, `linearize`, `version` |

## Quick Start

```bash
pip install -e .
python -m secp extract --tx-hex <raw-tx-hex>
```

From Python:

```python
from bitcoin import parse_tx, extract_signatures

tx_bytes = bytes.fromhex("<raw-tx-hex>")
tx, _ = parse_tx(tx_bytes)
records = extract_signatures(tx)
for rec in records:
    print(rec.vin, rec.sig.hex(), rec.script_type)
```

## Documentation Map

| Document | Content |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Package boundaries, dependency graph, design |
| [API.md](API.md) | Complete CLI and Python API reference |
| [MODULES.md](MODULES.md) | Every package: purpose, submodules, public API |
| [ALGORITHMS.md](ALGORITHMS.md) | DER parsing, sighash, ECC ops, linearization |
| [MATH.md](MATH.md) | Secp256k1 parameters, ECDSA math |
| [DATA_FLOW.md](DATA_FLOW.md) | Transaction → signature → coefficient flow |
| [CONFIGURATION.md](CONFIGURATION.md) | Settings, backends, env vars |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Runtime and dev dependencies |
| [TESTING.md](TESTING.md) | Test strategy, files, running tests |
| [GLOSSARY.md](GLOSSARY.md) | Domain terms and acronyms |

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
python -m pytest tests/ --benchmark-only
```
