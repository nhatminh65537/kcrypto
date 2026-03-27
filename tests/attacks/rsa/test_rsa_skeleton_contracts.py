"""Contract tests for RSA Tier 1 skeleton attacks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kcrypto.attacks.rsa.fermat_factorization import fermat_factorization
from kcrypto.attacks.rsa.know_d_factorization import known_d_factorization
from kcrypto.attacks.rsa.known_phi_factorization import known_phi_factorization
from kcrypto.attacks.rsa.wiener import wiener
from kcrypto.core.contracts import Result


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "rsa"
    / "sage_precomputed_rsa_attacks.json"
)


def _load_cases() -> dict[str, dict[str, object]]:
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return payload["cases"]


def test_sage_precomputed_values_are_internally_consistent() -> None:
    cases = _load_cases()

    for case_name in (
        "wiener",
        "fermat_factorization",
        "known_d_factorization",
        "known_phi_factorization",
    ):
        assert cases[case_name]["inputs"]["N"].bit_length() > 128

    wiener_case = cases["wiener"]
    wiener_inputs = wiener_case["inputs"]
    wiener_expected = wiener_case["expected"]
    assert wiener_expected["p"] * wiener_expected["q"] == wiener_inputs["N"]
    assert (wiener_expected["d"] * wiener_inputs["e"]) % wiener_expected["phi"] == 1
    assert pow(wiener_expected["m"], wiener_inputs["e"], wiener_inputs["N"]) == wiener_inputs["c"]

    fermat_case = cases["fermat_factorization"]
    fermat_inputs = fermat_case["inputs"]
    fermat_expected = fermat_case["expected"]
    assert fermat_expected["p"] * fermat_expected["q"] == fermat_inputs["N"]
    assert fermat_expected["a"] * fermat_expected["a"] - fermat_expected["b"] * fermat_expected["b"] == fermat_inputs["N"]

    known_d_case = cases["known_d_factorization"]
    known_d_inputs = known_d_case["inputs"]
    known_d_expected = known_d_case["expected"]
    assert known_d_expected["p"] * known_d_expected["q"] == known_d_inputs["N"]
    assert (known_d_inputs["e"] * known_d_inputs["d"]) % known_d_expected["phi"] == 1

    known_phi_case = cases["known_phi_factorization"]
    known_phi_inputs = known_phi_case["inputs"]
    known_phi_expected = known_phi_case["expected"]
    assert known_phi_expected["p"] * known_phi_expected["q"] == known_phi_inputs["N"]
    assert (known_phi_expected["p"] - 1) * (known_phi_expected["q"] - 1) == known_phi_inputs["phi"]
    assert known_phi_expected["p"] + known_phi_expected["q"] == known_phi_expected["sum_pq"]


@pytest.mark.parametrize(
    ("runner", "case_name", "expected_attack"),
    [
        (lambda case: wiener(**case["inputs"], verbose=False), "wiener", "rsa/wiener_attack"),
        (
            lambda case: known_d_factorization(**case["inputs"], verbose=False),
            "known_d_factorization",
            "rsa/known_d_factorization",
        ),
        (
            lambda case: known_phi_factorization(**case["inputs"], verbose=False),
            "known_phi_factorization",
            "rsa/known_phi_factorization",
        ),
    ],
)
def test_rsa_skeleton_attacks_return_result_placeholder(
    runner,
    case_name: str,
    expected_attack: str,
) -> None:
    case = _load_cases()[case_name]

    result = runner(case)

    assert isinstance(result, Result)
    assert result.success is False
    assert result.attack == expected_attack
    assert result.error == "Human implements"
    assert result.artifacts["tier"] == "T1"


@pytest.mark.parametrize(
    ("runner", "kwargs", "error_snippet"),
    [
        (wiener, {"e": 1, "N": 15, "c": None}, "greater than 1"),
        (fermat_factorization, {"N": 100, "max_iterations": 10}, "odd integer"),
        (known_d_factorization, {"N": 15, "e": 3, "d": 1}, "greater than 1"),
        (known_phi_factorization, {"N": 15, "phi": 1}, "greater than 1"),
    ],
)
def test_rsa_skeleton_attacks_validate_inputs(runner, kwargs: dict[str, int | None], error_snippet: str) -> None:
    result = runner(**kwargs, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert error_snippet in (result.error or "")


@pytest.mark.xfail(reason="Human implements RSA core math", strict=False)
def test_wiener_precomputed_case_expected_success_after_human_implementation() -> None:
    case = _load_cases()["wiener"]
    result = wiener(**case["inputs"], verbose=False)

    assert result.success is True
    assert result.data["d"] == case["expected"]["d"]


def test_fermat_precomputed_case_expected_success_after_human_implementation() -> None:
    case = _load_cases()["fermat_factorization"]
    result = fermat_factorization(**case["inputs"], verbose=False)

    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {
        case["expected"]["p"],
        case["expected"]["q"],
    }


@pytest.mark.xfail(reason="Human implements RSA core math", strict=False)
def test_known_d_precomputed_case_expected_success_after_human_implementation() -> None:
    case = _load_cases()["known_d_factorization"]
    result = known_d_factorization(**case["inputs"], verbose=False)

    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {
        case["expected"]["p"],
        case["expected"]["q"],
    }


@pytest.mark.xfail(reason="Human implements RSA core math", strict=False)
def test_known_phi_precomputed_case_expected_success_after_human_implementation() -> None:
    case = _load_cases()["known_phi_factorization"]
    result = known_phi_factorization(**case["inputs"], verbose=False)

    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {
        case["expected"]["p"],
        case["expected"]["q"],
    }
