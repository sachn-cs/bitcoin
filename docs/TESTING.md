# Testing

## Test Files

| File | Type | Coverage |
|------|------|----------|
| `bitcoin/tests/test_transaction.py` | Unit | Transaction parsing, extraction, sighash, edge cases |
| `bitcoin/tests/test_ecc.py` | Unit | Point ops, SEC encoding, backend dispatch |
| `bitcoin/tests/test_linear.py` | Unit | Linear coefficient derivation, error cases |
| `bitcoin/tests/test_psbt.py` | Unit | PSBT parsing and signature extraction |
| `bitcoin/tests/test_batch.py` | Unit | Batch processor, signature stream |
| `bitcoin/tests/test_config.py` | Unit | Config file loading, env var parsing |
| `bitcoin/tests/test_properties.py` | Property | Hypothesis-based algebraic invariants |
| `bitcoin/tests/test_benchmarks.py` | Benchmark | Performance benchmarks (not run by default) |

## Running Tests

```bash
# All tests
python -m pytest bitcoin/tests/

# Specific file
python -m pytest bitcoin/tests/test_ecc.py

# With coverage
python -m pytest bitcoin/tests/ --cov=bitcoin

# Property tests only
python -m pytest bitcoin/tests/test_properties.py -v

# Benchmarks (not collected by default)
python -m pytest bitcoin/tests/test_benchmarks.py --benchmark-only
```

## Test Strategy

**Unit tests** (`test_transaction.py`, `test_ecc.py`, `test_linear.py`, `test_psbt.py`, `test_batch.py`, `test_config.py`): Cover normal paths, edge cases, and error paths for each module. Use known-good test vectors (transactions from mainnet).

**Property-based tests** (`test_properties.py`): Use Hypothesis to verify algebraic invariants:
- `point_negate(point_negate(P)) == P`
- `point_add(P, Q) == point_add(Q, P)` (commutativity)
- `point_add(P, point_negate(P)) == INFINITY`
- `scalar_multiply(a, scalar_multiply(b, G)) == scalar_multiply(a*b, G)`
- `serialize_sec / parse_sec` round-trips
- DER parsing round-trips for valid signatures

## Critical Test Scenarios

1. **Transaction parsing**: SegWit and legacy transactions of varying complexity
2. **Sighash computation**: ALL, NONE, SINGLE, ANYONECANPAY combinations
3. **SIGHASH_SINGLE bug**: Sentinel `0x00...01` for missing output
4. **Taproot**: Key-path and script-path signature extraction
5. **PSBT**: Missing input values, zero-value digests
6. **ECC**: Point addition at infinity, curve membership validation
7. **Backend dispatch**: Pure Python vs coincurve, fallback logging
8. **Linearization**: Non-invertible r values, zero r/s rejection
9. **Batch**: Sequential and parallel (multiprocessing) processing
10. **Configuration**: Missing file, invalid format, env var overrides

## Coverage Gaps (Acceptable)

- **No fuzzing**: Binary fuzzing of transaction parser would be valuable but low ROI given well-defined Bitcoin protocol format
- **No integration tests**: Requires live network access; manual testing recommended
- **No concurrency tests**: Multiprocessing tested only by single test; race conditions in shared state are out of scope
