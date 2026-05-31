# Architecture

## High-Level Design

10 packages with strict one-way dependency. No package imports from a package at the same or deeper level in a way that creates a cycle.

```
field  →  curve  →  encoding  →  script  →  transaction  →  sighash  →  signature  →  psbt
                                                                                    │
                                                                                    ▼
                                                                               services  →  cli
```

## Package Boundaries

| Package | Files | Owns |
|---------|-------|------|
| `field` | `modular.py`, `sqrt.py` | Modular inverse, field square root, validation |
| `curve` | `point.py`, `operations.py`, `params.py`, `backend.py`, `native_backend.py`, `libsecp_backend.py`, `dispatch.py` | Point type, affine ops, SEC encoding, backend dispatch |
| `encoding` | `hex.py`, `binary.py`, `varint.py`, `der.py`, `sec.py`, `hasher.py` | Binary formats, DER/SEC parsing, SHA256, hash160 |
| `script` | `opcodes.py`, `parser.py`, `classifier.py`, `builder.py` | Script chunking, type classification, building |
| `transaction` | `models.py`, `parser.py`, `tx.py` | TxIn/TxOut/Tx structs, raw byte parsing, construction |
| `sighash` | `flag.py`, `legacy.py`, `segwit.py`, `taproot.py` | Sighash flag parsing, legacy/SegWit/Taproot digest |
| `signature` | `record.py`, `collection.py`, `check.py`, `extraction/engine.py`, `linearization/engine.py` | Record, extraction, verification, linearization |
| `psbt` | `models.py`, `parser.py` | PSBT structs, BIP-174 parsing |
| `services` | `serializer.py` | Transaction serialization |
| `cli` | `app.py` | Typer commands: `extract`, `linearize`, `version` |

## Layering Rules

1. `field` — stdlib only, no internal imports
2. `curve` — imports `field` only
3. `encoding` — stdlib only
4. `script` — imports `encoding` (for opcode values), `exceptions`
5. `transaction` — imports `encoding`, `exceptions`
6. `sighash` — imports `encoding`, `transaction`, `script`
7. `signature` — imports `curve`, `encoding`, `transaction`, `sighash`
8. `psbt` — imports `transaction`, `encoding`, `signature`
9. `services` — imports `transaction`, `encoding`
10. `cli` — imports `signature`, `encoding`, `transaction`

## Public Interface

The public API surface is defined in `bitcoin/__init__.py` with an explicit `__all__`. Every public symbol is re-exported from the top-level `bitcoin` package.

## Backend Architecture

Curve operations support pluggable backends:

- **NativeBackend** — pure Python implementation (always available, default)
- **LibsecpBackend** — wraps `coincurve` (libsecp256k1 C bindings, optional)

`set_backend(backend)` installs a backend; `get_backend()` returns it. All point operations (`add`, `double`, `multiply`, `negate`) dispatch through `curve/dispatch.py`.

## Key Design Decisions

- **Frozen dataclasses with slots** for all value objects (`Point`, `Tx`, `Record`, etc.)
- **Exhaustive type annotations** — no `Any` without documented reason, no `**kwargs`
- **Every file under 250 lines** except `__init__.py`
- **`__init__.py` is the public API surface** — submodules are implementation details
- **No backward-compatibility shims** — old flat modules (`ecc.py`, `linear.py`, etc.) and `_compat.py` have been removed
