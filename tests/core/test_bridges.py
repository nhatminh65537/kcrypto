"""Tests for optional dependency bridges."""

from __future__ import annotations

import importlib

import pytest

import kcrypto.bridges as bridges
from kcrypto.bridges import pwn as pwn_bridge
from kcrypto.bridges import sage as sage_bridge
from kcrypto.bridges import z3 as z3_bridge


@pytest.mark.parametrize(
    ("bridge_module", "flag_name"),
    [
        (sage_bridge, "SAGE_AVAILABLE"),
        (z3_bridge, "Z3_AVAILABLE"),
        (pwn_bridge, "PWN_AVAILABLE"),
    ],
)
def test_bridge_availability_flags_are_booleans(bridge_module, flag_name: str) -> None:
    value = getattr(bridge_module, flag_name)
    assert isinstance(value, bool)


def test_package_exports_bridge_modules() -> None:
    assert bridges.sage is sage_bridge
    assert bridges.z3 is z3_bridge
    assert bridges.pwn is pwn_bridge


def test_sage_bridge_all_is_minimal() -> None:
    exported = set(sage_bridge.__all__)

    assert "SAGE_AVAILABLE" in exported
    assert "require_sage" in exported
    assert "sage" in exported

@pytest.mark.parametrize(
    ("func", "module_name", "install_pkg"),
    [
        (sage_bridge.require_sage, "sage.all", "sagemath-standard"),
        (z3_bridge.require_z3, "z3", "z3-solver"),
        (pwn_bridge.require_pwn, "pwn", "pwntools"),
    ],
)
def test_require_functions_raise_actionable_error_when_dependency_missing(
    monkeypatch: pytest.MonkeyPatch,
    func,
    module_name: str,
    install_pkg: str,
) -> None:
    real_import_module = importlib.import_module

    def fake_import_module(name: str, package: str | None = None):
        if name == module_name:
            raise ImportError(f"No module named '{module_name}'")
        return real_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import_module)

    with pytest.raises(ImportError, match=install_pkg):
        func()
