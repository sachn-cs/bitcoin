"""Exception types for the bitcoin package."""


class NotInvertible(ValueError):
    """Raised when a value is not invertible in the given finite field."""


class PointError(ValueError):
    """Raised for invalid curve-point operations."""


class InvalidSignature(ValueError):
    """Raised when a signature is malformed or cannot be decoded."""


class InvalidDerSignature(ValueError):
    """Raised specifically for malformed DER-encoded signatures."""


class ParsingError(ValueError):
    """Raised when binary parsing fails."""


class InvalidSecp256k1PointError(ValueError):
    """Raised for invalid secp256k1 point operations."""


# ── Exception classes preserved from the original codebase ───────────
class NotInvertibleError(ValueError):
    """Raised when a linear coefficient is not invertible."""


class InvalidLinearCoefficientError(ValueError):
    """Raised for invalid linear coefficients."""


class NonInvertibleLinearCoefficientError(ValueError):
    """Raised when a linear coefficient cannot be inverted."""


class NoNonceReuseError(ValueError):
    """Raised when no nonce reuse is detected."""


class NonceReuseGroup:
    """Group of signatures sharing the same nonce."""


class RecoveredKey:
    """Represents a recovered private key from nonce reuse."""


class SameNonceError(ValueError):
    """Raised when two signatures share the same nonce."""


# ── Compatibility aliases (old → new) ─────────────────────────────────
BitcoinError = ValueError
InvalidDerSignatureError = InvalidDerSignature
InvalidHexError = ValueError
InvalidSecPublicKeyError = PointError
InvalidSighashFlagError = ValueError
MalformedVarintError = ParsingError
MissingInputValueError = ValueError
ScriptParseError = ParsingError
TruncatedTransactionError = ParsingError
UnsupportedScriptPathError = ValueError
