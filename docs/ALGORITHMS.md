# Algorithms

## DER Signature Parsing — `bitcoin/encoding/der.py`

Parse DER-encoded ECDSA signatures (BIP-66 strict).

`decode_der(sig_bytes) → (r: int, s: int)`

| Check | Condition | Error |
|-------|-----------|-------|
| Length | `9 ≤ len(sig) ≤ 73` | `InvalidDerSignature` |
| Sequence tag | `sig[0] == 0x30` | Missing sequence tag |
| Sequence length | `sig[1] == len(sig) - 2` | Inconsistent length |
| R integer tag | `sig[2] == 0x02` | Missing R tag |
| S integer tag | `sig[rend] == 0x02` | Missing S tag |
| No leading zeros | Value doesn't start with `0x00` unless next byte ≥ 0x80 | Leading zero |
| Non-negative | `value[0] & 0x80 == 0` | Negative integer |

Sighash byte is stripped before parsing (extraction engine handles this).

---

## Sighash Computation — `bitcoin/sighash/`

### Legacy Sighash (pre-SegWit)

`sighash_legacy(tx, input_index, script_code, sighash_flag) → bytes`

Payload: `version || varint(inputs) || inputs (with script_code at i) || varint(outputs) || outputs || locktime || sighash_flag`

**SINGLE bug**: if `base_type == SINGLE` and `input_index ≥ len(tx.outputs)`, returns `int_to_little_endian_bytes(1, 32)` per consensus rules.

### SegWit v0 (BIP-143)

`sighash_segwit(tx, input_index, script_code, amount, sighash_flag) → bytes`

Key differences from legacy:
- Amount serialized in payload (anti-fee-theft)
- Pre-computed `hash_prevouts`, `hash_sequence`, `hash_outputs`
- Anyone-can-pay zeros out `hash_prevouts` and `hash_sequence`

### Taproot (BIP-341)

`sighash_taproot(tx, input_index, script_code, amount, sighash_flag, script_pubkeys, spend_type, annex) → bytes`

Uses BIP-340 tagged hashes: `SHA256(SHA256(tag) || SHA256(tag) || data)`.

---

## ECC Point Arithmetic — `bitcoin/curve/operations.py`

### Point Negation

```
-P = (x, -y mod p)  for P = (x, y)
```

### Point Addition (affine)

```
m = (y₂ − y₁) / (x₂ − x₁) mod p
x₃ = m² − x₁ − x₂ mod p
y₃ = m(x₁ − x₃) − y₁ mod p
```

Edge cases: infinity, inverse (return infinity), equal points (double instead).

### Point Doubling (affine)

```
m = (3x₁² + a) / (2y₁) mod p   (a = 0 for secp256k1)
x₃ = m² − 2x₁ mod p
y₃ = m(x₁ − x₃) − y₁ mod p
```

### Scalar Multiplication (Montgomery ladder)

```
R0 = INFINITY
R1 = P
for each bit of scalar (MSB to LSB):
    if bit == 0: R1, R0 = R0 + R1, 2 * R0
    else:        R0, R1 = R0 + R1, 2 * R1
return R0
```

Constant-time in iterations. Scalar reduced modulo `CURVE_ORDER` first.

### Backend Dispatch

`negate`/`add`/`double`/`multiply` check `get_backend()` first; fall back to pure Python `_py` functions if no backend is installed.

---

## SEC Public Key Parsing — `bitcoin/encoding/sec.py`

### Compressed (33 bytes, prefix 0x02/0x03)

```
x = int.from_bytes(data[1:33], "big")
y = sqrt(x³ + 7 mod p)
if (y % 2) != expected_parity: y = (-y) % p
```

### Uncompressed (65 bytes, prefix 0x04)

```
x = int.from_bytes(data[1:33], "big")
y = int.from_bytes(data[33:], "big")
```

---

## Field Square Root — `bitcoin/field/sqrt.py`

Tonelli-Shanks specialization for p ≡ 3 (mod 4):

```
root = value^((p + 1) / 4) mod p
if root² mod p != value: raise NotInvertible
return root
```

Works because secp256k1's `p = 2²⁵⁶ − 2³² − 977` satisfies `p ≡ 3 (mod 4)`.

---

## Modular Inverse — `bitcoin/field/modular.py`

Extended Euclidean algorithm:

```
old_r, r = modulus, value
old_t, t = 0, 1
while r != 0:
    q = old_r // r
    old_r, r = r, old_r − q * r
    old_t, t = t, old_t − q * t
if old_r != 1: raise NotInvertible
return old_t % modulus
```

---

## Linearization — `bitcoin/signature/linearization/engine.py`

Given extracted (r, s, z):

```
α ≡ s · r⁻¹  (mod n)
β ≡ z · r⁻¹  (mod n)
```

Derived relation: `d' ≡ α · k (mod n)` where `d' = d + β`.
