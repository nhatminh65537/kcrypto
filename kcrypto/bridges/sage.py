"""Bridge helpers for optional SageMath integration."""

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


SAGE_AVAILABLE: Final[bool] = _has_module("sage.all")


def _missing_dependency_error() -> ImportError:
	"""Create a consistent, actionable missing-dependency error."""
	return ImportError(
		"SageMath is required for this feature. Install it with "
		"`pip install sagemath-standard`."
	)


class _MissingSage:
	"""Proxy object that fails only when Sage features are actually used."""

	def __getattr__(self, _name: str):
		raise _missing_dependency_error()

	def __call__(self, *args, **kwargs):
		raise _missing_dependency_error()


def require_sage():
	"""Import and return ``sage.all`` or raise a clear install hint.

	Returns:
		The imported ``sage.all`` module.

	Raises:
		ImportError: If SageMath is unavailable.
	"""
	try:
		return importlib.import_module("sage.all")
	except ImportError as exc:
		raise _missing_dependency_error() from exc


if SAGE_AVAILABLE:
	_sage_all = require_sage()
	matrix = _sage_all.matrix
	vector = _sage_all.vector
else:
	_missing = _MissingSage()
	matrix = _missing
	vector = _missing


__all__ = [
	"SAGE_AVAILABLE",
	"require_sage",
	"sage"
]
