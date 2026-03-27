"""Tests for lattice LLL wrapper attack."""

from __future__ import annotations

from kcrypto.attacks.lattice.lll import TIER, lll_reduce

from tests.attacks.lattice._fixture_utils import load_lattice_expected_values


def test_lll_reduce_matches_precomputed_sage_values() -> None:
    fixture = load_lattice_expected_values()

    result = lll_reduce(
        fixture["basis"],
        delta=fixture["lll"]["delta"],
        eta=fixture["lll"]["eta"],
        algorithm=fixture["lll"]["algorithm"],
    )

    assert result.success is True
    assert result.attack == "lattice/lll_reduction"
    assert result.data["reduced_basis"] == fixture["lll"]["reduced_basis"]
    assert result.data["dimension"] == 3


def test_lll_reduce_returns_failure_for_empty_basis() -> None:
    result = lll_reduce([])

    assert result.success is False
    assert "basis" in (result.error or "")


def test_lll_reduce_handles_edge_single_vector_basis() -> None:
    result = lll_reduce([[7, 0, 0]])

    assert result.success is True
    assert result.data["dimension"] == 1
    assert TIER == "T1"
