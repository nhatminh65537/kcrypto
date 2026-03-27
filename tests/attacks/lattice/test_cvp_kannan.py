"""Tests for Kannan CVP scaffold contract."""

from __future__ import annotations

import pytest

from kcrypto.attacks.lattice.cvp_kannan import TIER, cvp_kannan

from tests.attacks.lattice._fixture_utils import load_lattice_expected_values


def test_cvp_kannan_scaffold_returns_contract_failure() -> None:
    fixture = load_lattice_expected_values()

    result = cvp_kannan(fixture["basis"], fixture["target"])

    assert result.success is False
    assert result.attack == "lattice/cvp_kannan"
    assert "TODO" in (result.error or "")
    assert result.data["tier"] == "T1"


def test_cvp_kannan_edge_empty_inputs_still_return_result() -> None:
    result = cvp_kannan([], [])

    assert result.success is False
    assert result.data["basis_rows"] == 0
    assert result.data["target_dim"] == 0
    assert TIER == "T1"


@pytest.mark.xfail(reason="Waiting for human CVP Kannan implementation")
def test_cvp_kannan_matches_precomputed_sage_value_once_implemented() -> None:
    fixture = load_lattice_expected_values()

    result = cvp_kannan(fixture["basis"], fixture["target"])

    assert result.success is True
    assert result.data["closest_vector"] == fixture["cvp"]["kannan_embedding"]["closest_vector"]
    assert result.data["distance_sq"] == fixture["cvp"]["kannan_embedding"]["distance_sq"]
