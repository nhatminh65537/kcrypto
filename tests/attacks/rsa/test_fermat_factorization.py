"""Behavior tests for RSA Fermat factorization attack."""

from __future__ import annotations

from kcrypto.attacks.rsa.fermat_factorization import fermat_factorization
from kcrypto.core.contracts import Result


def test_fermat_factorization_success_for_close_primes() -> None:
    N = 101 * 103

    result = fermat_factorization(N=N, max_iterations=1000, verbose=False)

    assert isinstance(result, Result)
    assert result.success is True
    assert {result.data["p"], result.data["q"]} == {101, 103}
    assert result.attack == "rsa/fermat_factorization"


def test_fermat_factorization_rejects_even_modulus() -> None:
    result = fermat_factorization(N=100, max_iterations=100, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "odd integer" in (result.error or "")


def test_fermat_factorization_rejects_non_positive_modulus() -> None:
    result = fermat_factorization(N=1, max_iterations=100, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "odd integer" in (result.error or "")


def test_fermat_factorization_fails_on_prime_modulus_non_trivial_factor_requirement() -> None:
    result = fermat_factorization(N=13, max_iterations=20, verbose=False)

    assert isinstance(result, Result)
    assert result.success is False
    assert "non-trivial factors" in (result.error or "")
