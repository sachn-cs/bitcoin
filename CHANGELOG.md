# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2026-05-29

### Added
- CI/CD: GitHub Actions workflow (lint, typecheck, test on 3.12/3.13).
- `Makefile` with `lint`, `typecheck`, `test`, `test-cov`, `clean` targets.
- `py.typed` marker for PEP 561 typed-package distribution.
- `bitcoin/arithmetic.py`: shared `normalize_non_negative`, `inverse_mod`, `NotInvertibleError`.
- `TransformedPointRecord.validate()` method returning validation dict.
- Property-based tests for ECC operations and field arithmetic.
- Docstrings on all public functions across all modules.
- `CONTRIBUTING.md` and `LICENSE` (MIT).
- `dev` optional-dependencies group (`hypothesis`, `pytest`, `pytest-cov`, `ruff`, `mypy`).

### Changed
- `ecc.py` and `linear.py` deduplicated arithmetic via `arithmetic.py`.
- `signature.py`: pubkey parsing extracted to shared helpers to eliminate duplication.
- `serializer.py`: removed runtime imports of `SECP256K1_ORDER`/`is_on_curve`; delegates to `record.validate()`.
- Bumped version to 0.2.0.

### Fixed
- `models.py` is now a zero-import leaf module (no circular import risk).
- Validation no longer computed eagerly during serialization.

## [0.1.0] - 2026-05-20

### Added
- Initial release: tx parsing, signature extraction, ECC operations, CLI.
- Transform points pipeline (derive D' = d'G from related signatures).
- Linear coefficient derivation and verification.
- DER signature parsing, sighash computation, secp256k1 arithmetic.
