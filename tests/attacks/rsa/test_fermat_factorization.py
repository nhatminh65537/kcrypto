"""Tests for Fermat RSA factorization attack."""

from __future__ import annotations

from kcrypto.attacks.rsa.fermat_factorization import fermat_factorization
from kcrypto.core.contracts import Result

from tests.attacks.rsa._fixture_utils import assert_modulus_size, load_rsa_case


def test_fermat_fixture_consistency() -> None:
    case = load_rsa_case("fermat_factorization")
    inputs = case["inputs"]
    expected = case["expected"]

    assert_modulus_size(case)
    assert expected["p"] * expected["q"] == inputs["N"]
    assert expected["a"] * expected["a"] - expected["b"] * expected["b"] == inputs["N"]


def test_fermat_factorization_returns_result_contract() -> None:
    case = load_rsa_case("fermat_factorization")

    result = fermat_factorization(**case["inputs"], verbose=False)

    assert isinstance(result, Result)
    assert result.attack == "rsa/fermat_factorization"
    assert result.artifacts["tier"] == "T1"
    if result.success:
        assert result.error is None
    else:
        assert result.error


def test_fermat_factorization_validates_inputs() -> None:
    result = fermat_factorization(N=100, max_iterations=10, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "odd integer" in (result.error or "")


def test_fermat_factorization_matches_precomputed_expected_values() -> None:
    case = load_rsa_case("fermat_factorization")

    result = fermat_factorization(**case["inputs"], verbose=False)

    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {
        case["expected"]["p"],
        case["expected"]["q"],
    }
