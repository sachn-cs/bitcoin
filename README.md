# bitcoin

`bitcoin` is a small Python package for parsing raw Bitcoin transaction hex and extracting
the `r`, `s`, and `z` values from supported signature paths. It also derives linearized
ECDSA relations and lifts them into secp256k1 point space.

## Supported paths

- Legacy P2PKH
- Legacy P2SH multisig
- SegWit v0 P2WPKH
- SegWit v0 P2WSH multisig
- Nested SegWit v0 variants in P2SH

## Install

```bash
pip install .
```

## CLI

```bash
# Parse and pretty-print a raw transaction
python -m bitcoin.cli parse --tx <hex>

# Extract signatures (r, s, z) from a transaction
python -m bitcoin.cli extract --tx <hex>

# Derive linear ECDSA coefficients (α, β)
python -m bitcoin.cli linear --tx <hex>

# Derive point-space ECDSA relations (D + βG = αK)
python -m bitcoin.cli points --tx <hex>
```

SegWit inputs need spent output values to reconstruct `z`:

```bash
python -m bitcoin.cli extract --tx <hex> --input-values 100000000
```

## Python API

### Parse a transaction

```python
from bitcoin.transaction import Transaction

tx = Transaction.parse_hex(raw_transaction_hex)
```

### Extract signatures

SegWit v0 inputs need spent output values attached before extraction:

```python
tx = Transaction.parse_hex(raw_transaction_hex)
tx = tx.with_input_values([100000000])
collection = tx.extract()

print(collection.r)
print(collection.s)
print(collection.z)
```

### Linearize RSZ values

Derives the transformed ECDSA relation `d' ≡ αk (mod n)`:

```python
linear = tx.extract().linear()

print(linear.alpha)
print(linear.beta)
```

Starting from the standard identity `d ≡ (sk - z)r^{-1} (mod n)`, the code
computes `α ≡ sr^{-1}` and `β ≡ zr^{-1}` over the secp256k1 curve order.

### Point-space relations

Lifts the scalar relation into affine secp256k1 point arithmetic:

```python
relations = tx.extract().linear_points()
```

Given `D = dG`, `K = kG`, `B = βG`, the identity becomes `D + B = αK`.
All curve operations (point addition, doubling, scalar multiplication, SEC
parsing/serialization) are implemented manually in `bitcoin.ecc` using the
extended Euclidean algorithm for modular inversion.

## Development

### Setup

```bash
./setup.sh
```

Creates a virtual environment, installs the package in editable mode, installs
test and lint dependencies, and runs the test suite.

### Testing

```bash
python -m pytest tests/
```

The test suite covers parsing, all supported extraction paths, linearization,
point-space derivation, serialization, CLI integration, and edge cases.

### Linting and type checking

```bash
ruff check .
mypy bitcoin/ tests/
```

### Cleanup

```bash
./cleanup.sh
```

Removes build artifacts, caches, virtual environment, coverage data, and
`__pycache__` directories.
