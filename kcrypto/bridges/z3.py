"""Bridge helpers for optional z3 integration."""

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


Z3_AVAILABLE: Final[bool] = _has_module("z3")


def _missing_dependency_error() -> ImportError:
	"""Create a consistent, actionable missing-dependency error."""
	return ImportError(
		"z3-solver is required for this feature. Install it with "
		"`pip install z3-solver`."
	)


class _MissingZ3:
	"""Proxy object that fails only when z3 features are actually used."""

	def __getattr__(self, _name: str):
		raise _missing_dependency_error()

	def __call__(self, *args, **kwargs):
		raise _missing_dependency_error()


def require_z3():
	"""Import and return ``z3`` or raise a clear install hint.

	Returns:
		The imported ``z3`` module.

	Raises:
		ImportError: If z3 is unavailable.
	"""
	try:
		return importlib.import_module("z3")
	except ImportError as exc:
		raise _missing_dependency_error() from exc


z3 = require_z3() if Z3_AVAILABLE else _MissingZ3()


__all__ = ["Z3_AVAILABLE", "require_z3", "z3"]
