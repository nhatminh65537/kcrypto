"""Bridge helpers for optional pwntools integration."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Final


def _has_module(name: str) -> bool:
	"""Return True when the given module can be discovered."""
	try:
		return importlib.util.find_spec(name) is not None
	except ModuleNotFoundError:
		return False


PWN_AVAILABLE: Final[bool] = _has_module("pwn")


def _missing_dependency_error() -> ImportError:
	"""Create a consistent, actionable missing-dependency error."""
	return ImportError(
		"pwntools is required for this feature. Install it with "
		"`pip install pwntools`."
	)


class _MissingPwn:
	"""Proxy object that fails only when pwntools features are actually used."""

	def __getattr__(self, _name: str):
		raise _missing_dependency_error()

	def __call__(self, *args, **kwargs):
		raise _missing_dependency_error()


def require_pwn():
	"""Import and return ``pwn`` or raise a clear install hint.

	Returns:
		The imported ``pwn`` module.

	Raises:
		ImportError: If pwntools is unavailable.
	"""
	try:
		return importlib.import_module("pwn")
	except ImportError as exc:
		raise _missing_dependency_error() from exc


pwn = require_pwn() if PWN_AVAILABLE else _MissingPwn()


__all__ = ["PWN_AVAILABLE", "pwn", "require_pwn"]
