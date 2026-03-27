"""Tests for Wiener RSA attack contract and fixture behavior."""

from __future__ import annotations

import pytest

from kcrypto.attacks.rsa.wiener_attack import wiener_attack
from kcrypto.core.contracts import Result

from tests.attacks.rsa._fixture_utils import assert_modulus_size, load_rsa_case


def test_wiener_fixture_consistency() -> None:
    case = load_rsa_case("wiener")
    inputs = case["inputs"]
    expected = case["expected"]

    assert_modulus_size(case)
    assert expected["p"] * expected["q"] == inputs["N"]
    assert (expected["d"] * inputs["e"]) % expected["phi"] == 1
    assert pow(expected["m"], inputs["e"], inputs["N"]) == inputs["c"]


def test_wiener_attack_returns_result_contract() -> None:
    case = load_rsa_case("wiener")

    result = wiener_attack(**case["inputs"], verbose=False)

    assert isinstance(result, Result)
    assert result.attack == "rsa/wiener_attack"
    assert result.artifacts["tier"] == "T1"
    if result.success:
        assert result.error is None
    else:
        assert result.error


def test_wiener_attack_validates_inputs() -> None:
    result = wiener_attack(e=1, N=15, c=None, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "greater than 1" in (result.error or "")


@pytest.mark.xfail(reason="Waiting for stable human Wiener implementation", strict=False)
def test_wiener_attack_matches_precomputed_expected_values() -> None:
    case = load_rsa_case("wiener")

    result = wiener_attack(**case["inputs"], verbose=False)

    assert result.success is True
    assert result.data["d"] == case["expected"]["d"]
