"""CLI commands for the secp256k1 signing toolkit."""

from __future__ import annotations

from collections.abc import Sequence
from typing import List, Optional

import typer

from bitcoin.signature import extract_signatures, linearize_signatures
from bitcoin.signature.record import Record
from bitcoin.encoding.hex import decode_hex, encode_hex
from bitcoin.transaction import parse_tx

app = typer.Typer(name="secp")


def parse_input_values(value_str: str) -> list[int | None]:
    """Parse a comma-separated string of input values into integers.

    Empty entries (e.g. ``"100,,300"``) yield ``None``.
    """
    if not value_str or value_str.strip() == "":
        return []
    result: list[int | None] = []
    for part in value_str.split(","):
        part = part.strip()
        if part == "":
            result.append(None)
        else:
            result.append(int(part))
    return result


@app.command()
def extract(
    tx_hex: str = typer.Argument(..., help="Transaction hex"),
    utxo_scripts: Optional[List[str]] = typer.Option(
        None, "--utxo-script", help="UTXO scriptPubKey (one per input)"
    ),
    utxo_values: Optional[List[int]] = typer.Option(
        None, "--utxo-value", help="UTXO value in satoshis (one per input)"
    ),
) -> None:
    """Extract signatures from a transaction."""
    tx_bytes = decode_hex(tx_hex)
    tx, _ = parse_tx(tx_bytes)

    script_pubkeys = (
        [decode_hex(s) for s in utxo_scripts] if utxo_scripts else None
    )

    records = extract_signatures(tx, script_pubkeys, utxo_values)

    if not records:
        typer.echo("No signatures found.")
        raise typer.Exit(0)

    for rec in records:
        typer.echo(f"txid:  {encode_hex(rec.txid)}")
        typer.echo(f"vin:   {rec.vin}")
        typer.echo(f"sig:   {encode_hex(rec.sig)}")
        typer.echo(f"type:  {rec.script_type}")
        typer.echo(f"flag:  {rec.sighash_flag}")
        typer.echo(f"value: {rec.amount}")
        typer.echo("---")


@app.command()
def linearize(
    tx_hex: str = typer.Argument(..., help="Transaction hex"),
) -> None:
    """Extract and linearize signatures from a transaction."""
    tx_bytes = decode_hex(tx_hex)
    tx, _ = parse_tx(tx_bytes)
    records = extract_signatures(tx)
    sorted_records = linearize_signatures(records)

    for rec in sorted_records:
        typer.echo(f"{encode_hex(rec.txid)}:{rec.vin} {encode_hex(rec.sig)}")


@app.command()
def version() -> None:
    """Show the installed version."""
    from bitcoin import __version__ as ver

    typer.echo(f"secp v{ver}")


def main(args: Sequence[str] | None = None) -> int:
    """Entry point for the CLI."""
    if args is not None:
        app(args)
    else:
        app()
    return 0
