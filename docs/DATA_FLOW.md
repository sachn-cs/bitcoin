# Data Flow

## Request Flow

### 1. CLI Entry Point

```
CLI invocation
  → bitcoin.cli.main(args)
    → logging.basicConfig()
    → app(args, standalone_mode=False)  (typer)
      → parse() / extract() / linear() / points() / transform()
        → _resolve_transaction(tx_hex, input_values)
          → Transaction.parse_hex(tx_hex)
          → Transaction.with_input_values(parsed_values)
        → dispatch to command-specific serializer
```

### 2. Transaction Parsing

```
Transaction.parse_hex(hex_str)
  │
  ├─ utils.validate_hex_string()
  │   ├─ strips whitespace
  │   ├─ rejects empty / odd-length / non-hex characters
  │   └─ returns bytes
  │
  └─ parser.parse_transaction_bytes(raw_bytes)
      ├─ ByteReader (utils.py) for bounded reads
      ├─ version (4 bytes LE)
      ├─ segwit detection (marker 0x00 + flag != 0x00)
      ├─ input count (varint) + inputs (41+ bytes each)
      ├─ output count (varint) + outputs (9+ bytes each)
      ├─ witness data (if segwit)
      ├─ locktime (4 bytes LE)
      └─ trailing bytes check → TruncatedTransactionError
```

### 3. Transaction Structure

```
Transaction
  ├─ raw_bytes: bytes
  ├─ version: int
  ├─ segwit: bool
  ├─ inputs: tuple[TransactionInput, ...]
  │     └─ prevout_hash (32 bytes), prevout_index (uint32),
  │        script_sig (varbytes), sequence (uint32), witness (tuple)
  ├─ outputs: tuple[TransactionOutput, ...]
  │     └─ value (uint64), script_pubkey (varbytes)
  ├─ locktime: int
  └─ context: TransactionContext | None
        └─ input_values: tuple[int | None, ...]
```

### 4. Signature Extraction

```
Transaction.extract() / extract_signatures()
  │
  └─ for each input:
      │
      ├─ parse_script(txin.script_sig) → ScriptChunk[]
      ├─ chunks_to_pushes() → bytes[]
      │
      ├─ Taproot (witness + script_pubkey is taproot):
      │   ├─ key-path (1 witness item) → _extract_taproot_key_path
      │   │   ├─ parse_der_signature(witness[0])
      │   │   ├─ _resolve_input_value(context, index)
      │   │   └─ taproot_sighash(...)
      │   │
      │   └─ script-path → _extract_taproot_script_path
      │       ├─ witness[-2] = script, witness[:-2] = signatures
      │       ├─ parse_script(script) → pubkeys
      │       └─ taproot_sighash(..., spend_type=0xC0)
      │
      ├─ Legacy (no witness):
      │   ├─ P2PKH → _extract_legacy_p2pkh
      │   │   └─ pushes[0]=sig, pushes[1]=pubkey
      │   │   └─ legacy_sighash(..., make_p2pkh_script(pubkey))
      │   │
      │   └─ P2SH multisig → _extract_legacy_p2sh_multisig
      │       └─ pushes[:-1]=sigs, pushes[-1]=redeem script
      │       └─ legacy_sighash(..., redeem_script)
      │
      ├─ SegWit (no script_sig):
      │   ├─ P2WPKH → _extract_native_p2wpkh
      │   │   └─ witness[0]=sig, witness[1]=pubkey
      │   │   └─ segwit_sighash(..., amount)
      │   │
      │   └─ P2WSH multisig → _extract_native_p2wsh_multisig
      │       └─ witness[:-1]=sigs, witness[-1]=script
      │       └─ segwit_sighash(..., amount)
      │
      └─ P2SH-wrapped SegWit:
          ├─ P2SH-P2WPKH → _extract_p2sh_p2wpkh
          └─ P2SH-P2WSH → _extract_p2sh_p2wsh_multisig
```

### 5. Sighash Computation Flow

```
legacy_sighash(tx, index, script_code, flag)
  ├─ parse_sighash_flag(flag) → _SighashPlan
  ├─ check SINGLE + no matching output → return 0x00...01
  ├─ build input_chunks (substitute script_code at current input)
  ├─ build output_chunks (ALL / SINGLE / NONE dispatch)
  ├─ serialize version, varint(inputs), varint(outputs), locktime, flag
  └─ sha256d(payload)

segwit_sighash(tx, index, script_code, amount, flag)
  ├─ validate amount is not None
  ├─ parse_sighash_flag(flag) → _SighashPlan
  ├─ hash_prevouts (all prevouts or 0x00...00 for anyone-can-pay)
  ├─ hash_sequence (all sequences or 0x00...00)
  ├─ hash_outputs (ALL/SINGLE/NONE dispatch)
  └─ serialize + sha256d

taproot_sighash(tx, index, script_code, amount, flag, spks, ...)
  ├─ validate all input_values are non-None
  ├─ parse_sighash_flag(flag) → _SighashPlan
  ├─ sha_prevouts, sha_amounts, sha_scriptpubkeys, sha_sequences
  ├─ sha_outputs (ALL/SINGLE/NONE dispatch)
  ├─ hash_annex (0x00...00 if absent)
  └─ tagged_hash("TapSighash", payload)
```

### 6. Linearization Flow

```
SignatureCollection.linear()
  └─ derive_linear_coefficients(record) per record
      ├─ parse hex r, s, z → int
      ├─ validate: r ≠ 0, s ≠ 0, r < n, s < n
      ├─ r_inverse = inverse_mod(r, SECP256K1_ORDER)
      ├─ alpha = (s * r_inverse) % n
      └─ beta = (z * r_inverse) % n

SignatureCollection.linear_points()
  └─ derive_point_relation(record, pubkey_point)
      ├─ derive_linear_coefficients(record)
      ├─ point_b = scalar_multiply(beta, G)
      ├─ transformed_pk = point_add(pubkey_point, point_b)
      └─ return LinearPointRelation

SignatureCollection.transform_points()
  └─ derive_transformed_point(record, pubkey_point)
      ├─ same as linear_points
      └─ return TransformedPointRecord
```

## Batch Processing Flow

### Sequential (default)

```
batch_process(*txids, mp=False)
  └─ BatchProcessor.process_txids(txids)
      └─ for each txid:
          ├─ fetch_transaction(txid) → HTTP → blockstream.info
          ├─ optionally attach input values
          └─ Transaction.extract()
```

### Parallel (multiprocessing)

```
batch_process(*txids, mp=True)
  └─ multiprocessing.Pool
      └─ pool.map_async(worker, txids).get(timeout)
          └─ per worker:
              ├─ fetch_transaction(txid)
              └─ Transaction.extract()
```

## PSBT Flow

```
parse_psbt_hex(hex_str)
  └─ parse_psbt(raw_bytes)
      ├─ validate magic bytes "psbt\xff"
      ├─ parse global map (extract unsigned transaction)
      ├─ parse input maps (per input in unsigned tx)
      ├─ parse output maps (per output in unsigned tx)
      └─ return Psbt

psbt_extract_signatures(psbt, input_values)
  └─ for each psbt_in with partial_sigs:
      ├─ witness_utxo present → segwit sighash path
      ├─ non_witness_utxo present → legacy sighash path
      ├─ user-provided values → segwit fallback
      └─ no UTXO data → MissingInputValueError
```

## Configuration Flow

```
Config.load(path=None)
  ├─ if path provided: _load_file(path) → dict
  │   ├─ file missing → log ERROR, return {}
  │   └─ unsupported format → log ERROR, return {}
  ├─ override with env vars: _coerce(raw, type)
  │   ├─ bool: raw in {"1", "true", "yes"}
  │   ├─ int: int(raw) → ValueError on failure
  │   └─ str: raw as-is
  └─ Config(**kwargs)
```
