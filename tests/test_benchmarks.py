"""Benchmarks for ECC operations."""

from bitcoin.ecc import (
    SECP256K1_INFINITY,
    G,
    point_add,
    point_double,
    point_negate,
    scalar_multiply,
    serialize_sec_public_key,
)


def test_bench_point_add(benchmark) -> None:
    p1 = scalar_multiply(42, G)
    p2 = scalar_multiply(123, G)
    result = benchmark(point_add, p1, p2)
    assert not result.infinity


def test_bench_point_double(benchmark) -> None:
    p = scalar_multiply(42, G)
    result = benchmark(point_double, p)
    assert not result.infinity


def test_bench_scalar_multiply(benchmark) -> None:
    result = benchmark(scalar_multiply, 123456789, G)
    assert not result.infinity


def test_bench_scalar_multiply_large(benchmark) -> None:
    scalar = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141 - 2
    result = benchmark(scalar_multiply, scalar, G)
    assert not result.infinity


def test_bench_point_negate(benchmark) -> None:
    p = scalar_multiply(42, G)
    result = benchmark(point_negate, p)
    assert not result.infinity


def test_bench_serialize_compressed(benchmark) -> None:
    p = scalar_multiply(42, G)
    result = benchmark(serialize_sec_public_key, p, True)
    assert len(result) == 33


def test_bench_serialize_uncompressed(benchmark) -> None:
    p = scalar_multiply(42, G)
    result = benchmark(serialize_sec_public_key, p, False)
    assert len(result) == 65


def test_bench_infinity_add(benchmark) -> None:
    p = scalar_multiply(42, G)
    result = benchmark(point_add, SECP256K1_INFINITY, p)
    assert result == p
