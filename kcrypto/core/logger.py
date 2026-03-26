"""Logger contract scaffold used by attack/analyze modules."""

from __future__ import annotations

from typing import Protocol, cast


_LEVELS: dict[str, str] = {
    "step": ".",
    "found": "OK",
    "fail": "FAIL",
    "warn": "WARN",
}


class LoggerFn(Protocol):
    """Callable logger contract with level-specific helpers."""

    def __call__(self, msg: str, level: str = "step") -> None:
        """Log a message with the selected level marker."""

    def found(self, msg: str) -> None:
        """Log a successful discovery message."""

    def fail(self, msg: str) -> None:
        """Log a failure checkpoint message."""

    def warn(self, msg: str) -> None:
        """Log a warning message."""


def make_logger(name: str, verbose: bool) -> LoggerFn:
    """Create a logger compatible with kcrypto log semantics.

    Args:
        name: Attack/analyzer name used in output prefix.
        verbose: If False, logger should stay silent.

    Returns:
        A callable logger with helper methods: found, fail, warn.
    """

    def log(msg: str, level: str = "step") -> None:
        """Log message with standard marker when verbosity is enabled."""
        if not verbose:
            return
        marker = _LEVELS.get(level, _LEVELS["step"])
        print(f"[{name}] {marker} {msg}")

    def found(msg: str) -> None:
        """Log a successful discovery message."""
        log(msg, "found")

    def fail(msg: str) -> None:
        """Log a failure checkpoint message."""
        log(msg, "fail")

    def warn(msg: str) -> None:
        """Log a warning message."""
        log(msg, "warn")

    setattr(log, "found", found)
    setattr(log, "fail", fail)
    setattr(log, "warn", warn)
    return cast(LoggerFn, log)
