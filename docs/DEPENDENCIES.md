# Dependencies

## Runtime

| Package | Min Version | Purpose | Risk |
|---------|-------------|---------|------|
| `typer` | — | CLI framework | Low; well-maintained |
| `click` | — | Typer dependency | Low |

HTTP fetches use `urllib.request` from the Python stdlib — no `requests` or external HTTP library.

## Optional

| Package | Purpose |
|---------|---------|
| `coincurve` | C-based ECC via libsecp256k1 bindings (`LibsecpBackend`) |

Pure Python backend is always available and the default.

## Development

| Package | Purpose |
|---------|---------|
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |
| `pytest-benchmark` | Benchmarking |
| `mypy` | Static type checking |
| `ruff` | Linting |

## Not Required

- No cryptographic library for signing/verification — package only parses and extracts
- No `numpy` — all arithmetic is pure Python integer/bigint
- No `asyncio` — CLI is synchronous
