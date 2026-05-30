"""Tests for the config module."""

from __future__ import annotations

from bitcoin.config import Config


def test_config_defaults() -> None:
    cfg = Config()
    assert cfg.ecc_backend == "python"
    assert cfg.network == "mainnet"
    assert cfg.fetch_timeout == 30
    assert cfg.strict_parsing is True


def test_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("BITCOIN_ECC_BACKEND", "coincurve")
    monkeypatch.setenv("BITCOIN_NETWORK", "testnet")
    monkeypatch.setenv("BITCOIN_FETCH_TIMEOUT", "60")
    monkeypatch.setenv("BITCOIN_STRICT_PARSING", "false")
    cfg = Config.from_env()
    assert cfg.ecc_backend == "coincurve"
    assert cfg.network == "testnet"
    assert cfg.fetch_timeout == 60
    assert cfg.strict_parsing is False


def test_config_env_takes_precedence(monkeypatch, tmp_path) -> None:
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text('{"ecc_backend": "coincurve", "network": "testnet"}')
    monkeypatch.setenv("BITCOIN_NETWORK", "mainnet")
    cfg = Config.load(str(cfg_file))
    assert cfg.ecc_backend == "coincurve"
    assert cfg.network == "mainnet"
