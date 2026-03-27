"""Tests for known-phi RSA factorization attack."""

from __future__ import annotations

import pytest

from kcrypto.attacks.rsa.known_phi_factorization import known_phi_factorization
from kcrypto.core.contracts import Result

from tests.attacks.rsa._fixture_utils import assert_modulus_size, load_rsa_case


def test_known_phi_fixture_consistency() -> None:
    case = load_rsa_case("known_phi_factorization")
    inputs = case["inputs"]
    expected = case["expected"]

    assert_modulus_size(case)
    assert expected["p"] * expected["q"] == inputs["N"]
    assert (expected["p"] - 1) * (expected["q"] - 1) == inputs["phi"]
    assert expected["p"] + expected["q"] == expected["sum_pq"]


def test_known_phi_factorization_returns_result_contract() -> None:
    case = load_rsa_case("known_phi_factorization")

    result = known_phi_factorization(**case["inputs"], verbose=False)

    assert isinstance(result, Result)
    assert result.attack == "rsa/known_phi_factorization"
    assert result.artifacts["tier"] == "T1"
    if result.success:
        assert result.error is None
    else:
        assert result.error


def test_known_phi_factorization_validates_inputs() -> None:
    result = known_phi_factorization(N=15, phi=1, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "greater than 1" in (result.error or "")


@pytest.mark.xfail(reason="Waiting for stable human known-phi implementation", strict=False)
def test_known_phi_factorization_matches_precomputed_expected_values() -> None:
    case = load_rsa_case("known_phi_factorization")

    result = known_phi_factorization(**case["inputs"], verbose=False)

    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {
        case["expected"]["p"],
        case["expected"]["q"],
    }
