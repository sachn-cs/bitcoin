# Glossary

| Term | Definition |
|------|------------|
| **α (alpha)** | Linear coefficient `s * r⁻¹ mod n`. Rip van Winkle's linear relation `s = α * r` expressed as `α = s * r⁻¹ mod n`. |
| **β (beta)** | Linear coefficient `z * r⁻¹ mod n`. From the ECDSA signature equation `s = k⁻¹ * (z + r * d) mod n`, rearranged to `k = α + β * d` where `α` and `β` are derived from the extracted values. |
| **DER** | Distinguished Encoding Rules (ASN.1) — the binary format for ECDSA signatures in Bitcoin. |
| **ECDSA** | Elliptic Curve Digital Signature Algorithm — the signature scheme used by Bitcoin (pre-Taproot). |
| **Infinity** | The identity element of the elliptic curve group; `P + (-P) = O` (point at infinity). |
| **k** | Ephemeral (nonce) private key — a unique random scalar used per signature. |
| **Linearization** | The process of deriving (α, β) from (r, s, z) via modular arithmetic, expressing the underlying linear relation between the nonce and the private key. |
| **P2PKH** | Pay-to-Public-Key-Hash — legacy Bitcoin output locking funds to a hash of a public key. |
| **P2SH** | Pay-to-Script-Hash — output locking funds to a hash of a script. |
| **P2SH-P2WPKH** | P2SH-wrapped native SegWit P2WPKH (backward-compatible SegWit v0). |
| **P2SH-P2WSH** | P2SH-wrapped native SegWit P2WSH (backward-compatible SegWit multisig). |
| **P2WPKH** | Pay-to-Witness-Public-Key-Hash — native SegWit v0 single-signature output. |
| **P2WSH** | Pay-to-Witness-Script-Hash — native SegWit v0 multisig output. |
| **PSBT** | Partially Signed Bitcoin Transaction (BIP-174) — a standardized format for carrying unsigned transactions with accompanying signature data. |
| **r** | The x-coordinate of the ephemeral public key `kG` in an ECDSA signature. The first component of the `(r, s)` pair. |
| **s** | The second component of the ECDSA signature, computed as `s = k⁻¹ * (z + r * d) mod n`. |
| **secp256k1** | The elliptic curve used by Bitcoin: `y² = x³ + 7` over the field GF(p) where `p = 2²⁵⁶ - 2³² - 2⁹ - 2⁸ - 2⁷ - 2⁶ - 2⁴ - 1`. |
| **SEC** | Standards for Efficient Cryptography — encoding format for elliptic curve public keys (compressed or uncompressed). |
| **SegWit** | Segregated Witness — Bitcoin protocol upgrade separating transaction data from witness data (signatures). |
| **SIGHASH_ALL** | Sighash type `0x01`: sign all inputs and all outputs. |
| **SIGHASH_NONE** | Sighash type `0x02`: sign all inputs, no outputs. |
| **SIGHASH_SINGLE** | Sighash type `0x03`: sign all inputs, only the output at the same index as the input. |
| **SIGHASH_ANYONECANPAY** | Sighash modifier `0x80`: only sign the current input, not all inputs. |
| **Sighash** | The hash of the serialized transaction (with modified inputs/outputs per sighash flags) that is actually signed. |
| **Taproot** | Bitcoin protocol upgrade (v1 SegWit) enabling Schnorr signatures and MAST. |
| **Varint** | Variable-length integer format used in Bitcoin wire protocol. |
| **z** | The message hash — the sighash digest that is signed by the ECDSA signature. |
