# API Reference

## CLI — `bitcoin.cli`

```bash
python -m secp <command> [options]
```

### `extract`

Parse a raw transaction and extract all ECDSA signatures.

```bash
python -m secp extract <tx-hex> \
    [--utxo-script <hex>] \
    [--utxo-value <int>]
```

Output: per-signature lines with `txid`, `vin`, `sig`, `type`, `flag`, `value`.

### `linearize`

Extract and sort signatures by txid then vin.

```bash
python -m secp linearize <tx-hex>
```

### `version`

Print installed version.

```bash
python -m secp version
```

---

## Python SDK

All public symbols are available from `bitcoin`:

```python
import bitcoin
```

### Field Arithmetic

```python
from bitcoin import inverse, sqrt, pow_mod

assert inverse(3, 7) == 5          # 3 * 5 ≡ 1 (mod 7)
root = sqrt(42**2 % p, p)          # sqrt for p ≡ 3 mod 4
```

### Curve Operations

```python
from bitcoin import Point, GENERATOR, INFINITY, CURVE_ORDER
from bitcoin import negate, add, double, multiply, is_on_curve

p = Point(x=1, y=2)                           # affine point
inf = Point(infinity=True)                     # identity
assert is_on_curve(GENERATOR)
neg = negate(GENERATOR)
double_g = double(GENERATOR)                   # 2G
ten_g = multiply(10, GENERATOR)                # 10G

# SEC encoding
ser = GENERATOR.to_sec_compressed()            # 33 bytes
p2 = Point.from_sec_compressed(ser)
```

### Backend Selection

```python
from bitcoin import set_backend, get_backend, NativeBackend, LibsecpBackend

set_backend(NativeBackend())                   # pure Python (default)
# set_backend(LibsecpBackend())                # C-backed (pip install coincurve)
```

### Transaction Parsing

```python
from bitcoin import parse_tx, Tx, TxIn, TxOut, OutPoint, Witness, make_tx

# Parse raw bytes
tx_bytes = bytes.fromhex("<hex>")
tx, consumed = parse_tx(tx_bytes)              # → (Tx, int)

# Inspect
tx.version                                     # int
tx.inputs                                      # tuple[TxIn, ...]
tx.outputs                                     # tuple[TxOut, ...]
tx.lock_time                                   # int
tx.txid()                                      # bytes (LE double-SHA256)
tx.is_segwit()                                 # bool

# Build
tx = make_tx(version=2, inputs=[...], outputs=[...])
```

### Signature Extraction

```python
from bitcoin import extract_signatures, Record

records = extract_signatures(tx)               # → list[Record]

for rec in records:
    rec.txid                                    # bytes (32)
    rec.vin                                     # int
    rec.sig                                     # bytes (DER without sighash)
    rec.public_key                              # Point | bytes | None
    rec.script_type                             # str ("p2pkh", "p2wpkh", ...)
    rec.sighash_flag                            # int
    rec.amount                                  # int (sats)
```

### Signature Verification

```python
from bitcoin import verify_sig, linearize_signatures

assert verify_sig(message_hash, der_sig, public_key)

sorted_recs = linearize_signatures(records)     # sort by (txid, vin)
```

### PSBT

```python
from bitcoin import parse_psbt, serialize_psbt, Psbt

psbt = parse_psbt(raw_bytes)                   # → Psbt
psbt.unsigned_tx                                # Tx
psbt.inputs                                     # tuple[PsbtInput, ...]
psbt.outputs                                    # tuple[PsbtOutput, ...]

# Re-serialize
raw = serialize_psbt(psbt)
```

### Hashing

```python
from bitcoin import sha256, hash256, hash160, tagged_hash

sha256(b"data")                                 # 32 bytes
hash256(b"data")                                # double-SHA256
hash160(b"data")                                # RIPEMD160(SHA256(data))
tagged_hash("TapSighash", b"data")             # BIP-340 tagged hash
```

### Settings

```python
from bitcoin import settings

settings.strict_mode = True                     # raise on non-fatal issues
settings.default_backend = "native"             # or "libsecp" / None
settings.max_extraction_inputs = 5000
```

## Internal APIs (No Stability Guarantee)

- `bitcoin.field.modular`, `bitcoin.field.sqrt` — low-level arithmetic; use top-level `inverse`/`sqrt`
- `bitcoin.encoding.der`, `bitcoin.encoding.sec` — raw format parsers; use top-level `decode_der`/`parse_sec`
- `bitcoin.transaction.parser` — raw byte parsing; use `parse_tx`
- `bitcoin.sighash.legacy`, `bitcoin.sighash.segwit`, `bitcoin.sighash.taproot` — use top-level `sighash_legacy`/`sighash_segwit`/`sighash_taproot`
- `bitcoin.signature.extraction.engine` — extraction internals; use `extract_signatures`
