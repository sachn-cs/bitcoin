# Testing

## Test Files

| File | Package Coverage |
|------|------------------|
| `tests/test_field.py` | Field arithmetic: inverse, sqrt, validation |
| `tests/test_curve.py` | Point ops, SEC roundtrip, backend dispatch |
| `tests/test_encoding.py` | Hex, varint, DER, SEC, hashing, binary |
| `tests/test_transaction_new.py` | Tx models: OutPoint, Witness, TxIn, TxOut, Tx |
| `tests/test_signature_new.py` | Record, verification, linearization |
| `tests/test_imports.py` | All public imports, no circular deps |
| `tests/test_config.py` | Settings (if applicable) |
| `tests/test_benchmarks.py` | Performance benchmarks (not run by default) |

## Running Tests

```bash
# All tests
python -m pytest tests/

# Specific file
python -m pytest tests/test_curve.py -v

# With coverage
python -m pytest tests/ --cov=bitcoin

# Benchmarks
python -m pytest tests/test_benchmarks.py --benchmark-only
```

## Test Strategy

**Unit tests**: Cover normal paths, edge cases, and error paths for each package. Use known-good test vectors where applicable.

**Property-based tests**: Algebraic invariants for point ops, DER roundtrip, SEC roundtrip, field ops.

## Critical Scenarios

1. **Transaction parsing**: SegWit and legacy, edge cases (no inputs, no outputs)
2. **Sighash**: ALL, NONE, SINGLE, ANYONECANPAY combinations; SINGLE bug sentinel
3. **ECC**: Infinity handling, curve membership, SEC roundtrip
4. **Backend dispatch**: Native vs libsecp, fallback
5. **Signature extraction**: P2PKH, P2WPKH, P2WSH, P2SH-P2WPKH, Taproot
6. **Linearization**: Non-invertible r, zero r/s rejection
7. **PSBT**: Parse roundtrip, partial sigs
8. **Configuration**: Settings defaults, validation

## Coverage Gaps

- No integration tests (require live network)
- No async tests
- No fuzzing (low ROI for Bitcoin's well-defined protocol)
