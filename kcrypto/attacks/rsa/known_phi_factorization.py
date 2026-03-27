"""Recover RSA prime factors from known ``phi(N)`` (Tier 1)."""

from __future__ import annotations

import math
from time import perf_counter

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger


TIER = "T1"
ATTACK_KEY = "rsa/known_phi_factorization"


def known_phi_factorization(N: int, phi: int, *, verbose: bool = False) -> Result:
    """Factor ``N`` using the identity between ``N``, ``phi(N)``, and ``p + q``.

    Tier:
        T1 (pure function).

    Applicability:
        Use when both modulus ``N`` and Euler totient ``phi`` are available.

    Failure Mode:
        Returns ``Result(success=False, error=...)`` for invalid input or when
        the quadratic discriminant does not produce integer roots.

    Success Data Keys:
        p: First recovered prime factor.
        q: Second recovered prime factor.
        sum_pq: Recovered value of ``p + q``.

    Args:
        N: RSA modulus.
        phi: Euler totient of ``N``.
        verbose: If True, emit checkpoint logs.

    Returns:
        Result contract containing attack status, outputs, and metadata.
    """
    started = perf_counter()
    log = make_logger("known_phi_factorization", verbose)
    log("validate inputs")

    if N <= 1 or phi <= 1:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("N and phi must be integers greater than 1")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={"tier": TIER, "inputs": {"N": N, "phi": phi}},
            error="N and phi must be integers greater than 1.",
            elapsed=elapsed_ms,
        )

    # TODO(Human): implement known-phi factorization core math.
    sum_pq = N - phi + 1

    D = sum_pq**2 - 4 * N
    if D < 0:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("negative discriminant, no real roots for p and q")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={"tier": TIER, "inputs": {"N": N, "phi": phi}},
            error="negative discriminant, no real roots for p and q",
            elapsed=elapsed_ms,
        )
    
    if D == 0:
        log.warn("discriminant is zero, repeated prime factors p and q are equal")
        p = q = sum_pq // 2
        elapsed_ms = (perf_counter() - started) * 1000.0
        return Result(
            success=True,
            attack=ATTACK_KEY,
            data={"p": p, "q": q, "sum_pq": sum_pq},
            artifacts={"tier": TIER, "inputs": {"N": N, "phi": phi}},
            error=None,
            elapsed=elapsed_ms,
        )

    sqrtD = math.isqrt(D)
    if sqrtD * sqrtD != D:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("discriminant is not a perfect square, no integer roots for p and q")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={"tier": TIER, "inputs": {"N": N, "phi": phi}},
            error="discriminant is not a perfect square, no integer roots for p and q",
            elapsed=elapsed_ms,
        )
    
    p = (sum_pq + sqrtD) // 2
    q = (sum_pq - sqrtD) // 2
    elapsed_ms = (perf_counter() - started) * 1000.0
    log.found("factors found")
    return Result(
        success=True,
        attack=ATTACK_KEY,
        data={"p": p, "q": q, "sum_pq": sum_pq},
        artifacts={"tier": TIER, "inputs": {"N": N, "phi": phi}},
        error=None,
        elapsed=elapsed_ms,
    )