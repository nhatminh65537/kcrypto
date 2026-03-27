"""Tests for lattice BKZ wrapper attack."""

from __future__ import annotations

from kcrypto.attacks.lattice.bkz import TIER, bkz_reduce

from tests.attacks.lattice._fixture_utils import load_lattice_expected_values


def test_bkz_reduce_matches_precomputed_sage_values() -> None:
    fixture = load_lattice_expected_values()

    result = bkz_reduce(
        fixture["basis"],
        block_size=fixture["bkz"]["block_size"],
        algorithm=fixture["bkz"]["algorithm"],
    )

    assert result.success is True
    assert result.attack == "lattice/bkz_reduction"
    assert result.data["reduced_basis"] == fixture["bkz"]["reduced_basis"]
    assert result.data["block_size"] == 2


def test_bkz_reduce_returns_failure_for_invalid_block_size() -> None:
    fixture = load_lattice_expected_values()

    result = bkz_reduce(fixture["basis"], block_size=1)

    assert result.success is False
    assert "block_size" in (result.error or "")


def test_bkz_reduce_returns_failure_for_empty_basis() -> None:
    result = bkz_reduce([], block_size=2)

    assert result.success is False
    assert "basis" in (result.error or "")
    assert TIER == "T1"
