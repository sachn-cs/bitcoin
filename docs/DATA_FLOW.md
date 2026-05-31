# Data Flow

## CLI Invocation

```
python -m secp extract <tx-hex> [--utxo-script ...] [--utxo-value ...]
  → cli.app.main()
    → decode_hex(tx_hex)
    → parse_tx(tx_bytes)          → (Tx, bytes_consumed)
    → extract_signatures(tx, script_pubkeys, values)
      → for each input:
          parse_script(script_sig) → classify → dispatch
          → Record(txid, vin, sig, pubkey, type, flag, amount)
    → print records
```

## Transaction Parsing

`parse_tx(bytes) → (Tx, bytes_consumed)`

```
  ByteReader(raw_bytes)
  ├── version               (4 bytes LE)
  ├── segwit detection       (marker 0x00 + flag ≠ 0x00)
  ├── input count (varint) + inputs (OutPoint + script_sig + sequence + witness)
  ├── output count (varint) + outputs (value + script_pubkey)
  ├── witness data (if segwit)
  ├── locktime              (4 bytes LE)
  └── trailing bytes check
```

## Signature Extraction

```
extract_signatures(tx, utxo_scripts, utxo_values)
  │
  └─ for each input:
      │
      ├─ parse_script(txin.script_sig) → list of elements
      ├─ classify_script_pubkey(script_pubkey)
      │
      ├─ Legacy (no witness):
      │   ├─ P2PKH: script_sig pushes[0]=sig, pushes[1]=pubkey
      │   │          sighash = legacy(tx, vin, p2pkh_script, flag)
      │   │          recover pubkey from sighash + sig
      │   │
      │   └─ P2SH multisig: pushes[:-1]=sigs, pushes[-1]=redeem script
      │
      ├─ SegWit (witness present):
      │   ├─ P2WPKH: witness[0]=sig, witness[1]=pubkey
      │   │            sighash = segwit(tx, vin, script_code, value, flag)
      │   │
      │   ├─ P2WSH: witness[:-1]=sigs, witness[-1]=script
      │   │
      │   └─ P2SH-P2WPKH / P2SH-P2WSH:
      │       script_sig = redeem script, witness has sigs
      │
      └─ Record(..., sighash computed, pubkey recovered)
```

## Sighash Computation

### Legacy

`legacy_sighash(tx, index, script_code, flag)`
- Parse flag → base_type + anyone_can_pay
- Check SINGLE + no matching output → return 0x00...01 (consensus sentinel)
- Substitute `script_code` at current input
- Serialize: `version || inputs || outputs || locktime || flag`
- SHA256(SHA256(payload))

### SegWit v0 (BIP-143)

`segwit_sighash(tx, index, script_code, amount, flag)`
- Validate amount is not None
- Pre-compute `hash_prevouts`, `hash_sequence`, `hash_outputs`
- Anyone-can-pay → `hash_prevouts = hash_sequence = 0x00...00`
- Payload includes amount (prevents fee theft)

## Linearization

```
linearize_signatures(records)
  └─ sort by (txid, vin)
  └─ for each record:
      r_inv = inverse_mod(r, CURVE_ORDER)
      alpha = (s * r_inv) % n
      beta  = (z * r_inv) % n
```
