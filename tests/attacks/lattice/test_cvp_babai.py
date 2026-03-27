"""Tests for Babai CVP scaffold contract."""

from __future__ import annotations

import pytest

from kcrypto.attacks.lattice.cvp_babai import TIER, cvp_babai

from tests.attacks.lattice._fixture_utils import load_lattice_expected_values


def test_cvp_babai_scaffold_returns_contract_failure() -> None:
    fixture = load_lattice_expected_values()

    result = cvp_babai(fixture["basis"], fixture["target"])

    assert result.success is False
    assert result.attack == "lattice/cvp_babai"
    assert "TODO" in (result.error or "")
    assert result.data["tier"] == "T1"


def test_cvp_babai_edge_empty_inputs_still_return_result() -> None:
    result = cvp_babai([], [])

    assert result.success is False
    assert result.data["basis_rows"] == 0
    assert result.data["target_dim"] == 0
    assert TIER == "T1"


@pytest.mark.xfail(reason="Waiting for human CVP Babai implementation")
def test_cvp_babai_matches_precomputed_sage_value_once_implemented() -> None:
    fixture = load_lattice_expected_values()

    result = cvp_babai(fixture["basis"], fixture["target"])

    assert result.success is True
    assert result.data["closest_vector"] == fixture["cvp"]["babai_nearest_plane"]["closest_vector"]
    assert result.data["distance_sq"] == fixture["cvp"]["babai_nearest_plane"]["distance_sq"]
