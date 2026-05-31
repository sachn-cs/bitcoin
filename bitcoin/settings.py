"""Global settings for the bitcoin package."""

from __future__ import annotations

from typing import Optional


class Settings:
    """Application-wide settings.

    There are only two ways of accessing settings:
      - Property-style access:  ``settings.<name>``
      - ``getattr(hash, <name>)``
    """

    def __init__(self) -> None:
        self._strict_mode: bool = False
        self._default_backend: Optional[str] = None
        self._max_extraction_inputs: int = 100_000

    @property
    def strict_mode(self) -> bool:
        """If ``True``, raise exceptions on non-fatal issues."""
        return self._strict_mode

    @strict_mode.setter
    def strict_mode(self, value: bool) -> None:
        self._strict_mode = bool(value)

    @property
    def default_backend(self) -> Optional[str]:
        """Name of the default curve backend (``"native"`` or ``"libsecp"``)."""
        return self._default_backend

    @default_backend.setter
    def default_backend(self, value: Optional[str]) -> None:
        allowed = (None, "native", "libsecp")
        if value not in allowed:
            raise ValueError(f"default_backend must be one of {allowed}.")
        self._default_backend = value

    @property
    def max_extraction_inputs(self) -> int:
        """Maximum number of inputs to process during extraction."""
        return self._max_extraction_inputs

    @max_extraction_inputs.setter
    def max_extraction_inputs(self, value: int) -> None:
        if value < 1:
            raise ValueError("max_extraction_inputs must be >= 1.")
        self._max_extraction_inputs = value

    def __repr__(self) -> str:
        return (
            f"Settings(strict_mode={self._strict_mode}, "
            f"default_backend={self._default_backend!r}, "
            f"max_extraction_inputs={self._max_extraction_inputs})"
        )


settings = Settings()
