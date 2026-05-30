# Mathematics

## Secp256k1 Parameters

### Field Prime

```
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
```

The underlying finite field is GF(p). All point coordinates are field elements.

### Curve Order

```
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
```

The number of points on the curve (prime order). All scalar arithmetic is modulo `n`.

### Curve Equation

```
y² = x³ + 7   (mod p)
```

Coefficient `a = 0`, coefficient `b = 7`. This is a Koblitz curve (secp256k1).

### Generator Point

```
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
```

## ECDSA Signature

A valid ECDSA signature `(r, s)` over a message `m` with private key `d` and nonce `k`:

```
k = random nonce in [1, n-1]
R = k × G
r = R.x  (mod n)         # if r = 0, choose new k
z = hash(m)              # truncated to curve order bit length
s = k⁻¹ × (z + r × d)   (mod n)
```

## Extracted Values

From a raw transaction, the extraction process recovers:

| Variable | Source | Description |
|----------|--------|-------------|
| `r` | DER signature | First integer in the DER sequence |
| `s` | DER signature | Second integer in the DER sequence |
| `z` | Reconstructed sighash | Computed via `legacy_sighash()`, `segwit_sighash()`, or `taproot_sighash()` |
| `sighash_flag` | Last byte of raw signature | Determines which outputs/inputs are covered |

## Linearization

Starting from the standard ECDSA verification equation:

```
s ≡ k⁻¹ × (z + r × d)  (mod n)
```

Rearranging to express `d`:

```
sk ≡ z + rd  (mod n)
d ≡ (sk - z) × r⁻¹  (mod n)
d ≡ s × k × r⁻¹ - z × r⁻¹  (mod n)
d ≡ (s × r⁻¹) × k - (z × r⁻¹)  (mod n)
```

Define:

```
α ≡ s × r⁻¹  (mod n)
β ≡ z × r⁻¹  (mod n)
```

Then:

```
d ≡ αk - β  (mod n)
d + β ≡ αk  (mod n)
```

This is the **scalar relation**: `d' ≡ αk (mod n)` where `d' = d + β`.

## Point-Space Relation

Lifting the scalar relation to secp256k1 point arithmetic:

```
D' = d' × G
   = (αk) × G
   = α × (k × G)
   = α × K
```

Where `K = k × G` is the nonce point (public nonce).

The complete relation:

```
D' = D + βG = αK
```

Where:
- `D = d × G` is the public key
- `βG = β × G` is the offset point
- `K = k × G` is the nonce point

## Transformed Point

The transformed private key and point:

```
d' ≡ d + β  (mod n)
D' = D + βG = d' × G
```

This is used in `derive_transformed_point()` which returns the point `D'` directly without requiring knowledge of `k` or `K`.

## Field Arithmetic

### Modular Inverse (Extended Euclidean Algorithm)

For inputs `value` and `modulus`:

```
Input:  a = modulus, b = value
Output: b⁻¹ mod a (if gcd(a, b) = 1)

Initialize:
    old_r, r = a, b
    old_t, t = 0, 1

While r ≠ 0:
    quotient = old_r // r
    old_r, r = r, old_r - quotient × r
    old_t, t = t, old_t - quotient × t

If old_r ≠ 1:
    raise NotInvertibleError

Return old_t mod a
```

### Field Square Root (Tonelli-Shanks for p ≡ 3 mod 4)

Since secp256k1's field prime satisfies `p ≡ 3 (mod 4)`:

```
√v = v^((p+1)/4)  mod p
```

This works because when `p ≡ 3 (mod 4)`:

```
(v^((p+1)/4))² ≡ v^((p+1)/2) ≡ v × v^((p-1)/2) ≡ v × (v/p)  (mod p)
```

Where `(v/p)` is the Legendre symbol, which is 1 when `v` is a quadratic residue.
