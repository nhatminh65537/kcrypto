"""Tests for known-d RSA factorization attack."""

from __future__ import annotations

import pytest

from kcrypto.attacks.rsa.known_d_factorization import known_d_factorization
from kcrypto.core.contracts import Result

from tests.attacks.rsa._fixture_utils import assert_modulus_size, load_rsa_case


def test_known_d_fixture_consistency() -> None:
    case = load_rsa_case("known_d_factorization")
    inputs = case["inputs"]
    expected = case["expected"]

    assert_modulus_size(case)
    assert expected["p"] * expected["q"] == inputs["N"]
    assert (inputs["e"] * inputs["d"]) % expected["phi"] == 1


def test_known_d_factorization_returns_result_contract() -> None:
    case = load_rsa_case("known_d_factorization")

    result = known_d_factorization(**case["inputs"], verbose=False)

    assert isinstance(result, Result)
    assert result.attack == "rsa/known_d_factorization"
    assert result.artifacts["tier"] == "T1"
    if result.success:
        assert result.error is None
    else:
        assert result.error


def test_known_d_factorization_validates_inputs() -> None:
    result = known_d_factorization(N=15, e=3, d=1, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "greater than 1" in (result.error or "")


@pytest.mark.xfail(reason="Waiting for stable human known-d implementation", strict=False)
def test_known_d_factorization_matches_precomputed_expected_values() -> None:
    case = load_rsa_case("known_d_factorization")

    result = known_d_factorization(**case["inputs"], verbose=False)

    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {
        case["expected"]["p"],
        case["expected"]["q"],
    }
