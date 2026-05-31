"""Hash-function wrappers used by Bitcoin."""

import hashlib


def sha256(data: bytes) -> bytes:
    """Return the SHA-256 digest of *data*."""
    return hashlib.sha256(data).digest()


def hash256(data: bytes) -> bytes:
    """Return the double-SHA-256 digest of *data*.

    This is used for transaction hashing (txid, wtxid).
    """
    return sha256(sha256(data))


def hash160(data: bytes) -> bytes:
    """Return the HASH-160 (SHA-256 then RIPEMD-160) digest."""
    return hashlib.new("ripemd160", sha256(data)).digest()  # type: ignore[arg-type]


def tagged_hash(tag: str, data: bytes) -> bytes:
    """Return the BIP-340 tagged hash ``SHA256(SHA256(tag) || SHA256(tag) || data)``.

    Used for Taproot signing.
    """
    tag_hash = sha256(tag.encode())
    return sha256(tag_hash + tag_hash + data)
