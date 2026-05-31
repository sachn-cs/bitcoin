"""Modular arithmetic over finite fields: inversion and validation."""

from bitcoin.exceptions import NotInvertible


def inverse(value: int, modulus: int) -> int:
    """Return the modular inverse of *value* modulo *modulus*.

    Uses the extended Euclidean algorithm.

    Raises:
        TypeError: If either argument is not an ``int``.
        ValueError: If *modulus* is ≤ 1 or *value* is negative.
        NotInvertible: If *value* and *modulus* are not coprime.
    """
    t_value, t_modulus = type(value), type(modulus)
    if t_value is not int:
        raise TypeError(f"Value must be int, got {t_value.__name__}.")
    if not isinstance(modulus, int):
        raise TypeError(f"Modulus must be int, got {t_modulus.__name__}.")
    if modulus <= 1:
        raise ValueError(f"Modulus must be > 1, got {modulus}.")
    if value < 0:
        raise ValueError(f"Value must be non-negative, got {value}.")
    if value == 0:
        raise NotInvertible("Zero has no modular inverse.")

    old_r, r = modulus, value
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_t, t = t, old_t - quotient * t

    if old_r != 1:
        raise NotInvertible(
            f"Value {value} is not invertible modulo {modulus}."
        )
    return old_t % modulus


def validate_non_negative(value: int, label: str = "value") -> int:
    """Return *value* unchanged if it is a non-negative ``int``.

    Raises:
        TypeError: If *value* is not an ``int``.
        ValueError: If *value* is negative.
    """
    if type(value) is not int:
        raise TypeError(f"{label} must be an int, got {type(value).__name__}.")
    if value < 0:
        raise ValueError(f"{label} must be non-negative, got {value}.")
    return value
