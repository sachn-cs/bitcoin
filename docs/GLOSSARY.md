# Glossary

| Term | Definition |
|------|------------|
| **α (alpha)** | Linear coefficient `s·r⁻¹ mod n`. |
| **β (beta)** | Linear coefficient `z·r⁻¹ mod n`. |
| **DER** | Distinguished Encoding Rules (ASN.1) — binary format for ECDSA signatures in Bitcoin. |
| **ECDSA** | Elliptic Curve Digital Signature Algorithm — signature scheme used by Bitcoin (pre-Taproot). |
| **Infinity** | Identity element of the elliptic curve group; `P + (−P) = O`. |
| **k** | Ephemeral (nonce) private key — unique random scalar per signature. |
| **Linearization** | Deriving (α, β) from (r, s, z) via modular arithmetic. |
| **P2PKH** | Pay-to-Public-Key-Hash — legacy output. |
| **P2SH** | Pay-to-Script-Hash — output locked to script hash. |
| **P2SH-P2WPKH** | P2SH-wrapped native SegWit P2WPKH. |
| **P2SH-P2WSH** | P2SH-wrapped native SegWit P2WSH. |
| **P2WPKH** | Pay-to-Witness-Public-Key-Hash — native SegWit v0. |
| **P2WSH** | Pay-to-Witness-Script-Hash — native SegWit v0 multisig. |
| **PSBT** | Partially Signed Bitcoin Transaction (BIP-174). |
| **r** | x-coordinate of ephemeral public key `kG`. First component of `(r, s)`. |
| **s** | `s = k⁻¹·(z + r·d) mod n`. Second component of `(r, s)`. |
| **secp256k1** | Elliptic curve `y² = x³ + 7` over GF(p), `p = 2²⁵⁶ − 2³² − 977`. |
| **SEC** | Standards for Efficient Cryptography — public key encoding (compressed/uncompressed). |
| **SegWit** | Segregated Witness — Bitcoin upgrade separating witness data from transaction data. |
| **Sighash** | Hash of the serialized transaction (with modifications per sighash flags) that is signed. |
| **Taproot** | Bitcoin v1 SegWit upgrade enabling Schnorr signatures and MAST. |
| **Varint** | Variable-length integer format in Bitcoin wire protocol. |
| **z** | Message hash — the sighash digest signed by the ECDSA signature. |
