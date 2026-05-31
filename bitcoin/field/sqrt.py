"""Field square root via Tonelli-Shanks for p ≡ 3 (mod 4)."""

from bitcoin.exceptions import PointError


def pow_mod(value: int, exponent: int, modulus: int) -> int:
    """Return ``pow(value, exponent, modulus)``.

    Exists as a named wrapper so callers can mock or trace modular
    exponentiation independently of the builtin.
    """
    return pow(value, exponent, modulus)


def sqrt(value: int, field_prime: int) -> int:
    """Return a square root of *value* in GF(*field_prime*).

    Works when *field_prime* ≡ 3 (mod 4), which secp256k1 satisfies.

    Raises:
        PointError: If *value* is not a quadratic residue.
    """
    root = pow_mod(value, (field_prime + 1) // 4, field_prime)
    if (root * root) % field_prime != value % field_prime:
        raise PointError(f"No square root for value modulo {field_prime}.")
    return root
