"""Recover RSA factors from a known private exponent (Tier 1)."""

from __future__ import annotations

from time import perf_counter

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger
import random
import math


TIER = "T1"
ATTACK_KEY = "rsa/known_d_factorization"


def known_d_factorization(N: int, e: int, d: int, *, max_trails: int = 100, verbose: bool = False) -> Result:
    """Factor ``N`` when RSA exponents ``e`` and ``d`` are both known.

    Tier:
        T1 (pure function).

    Applicability:
        This method is applicable when a valid private exponent is already
        available and the goal is to recover prime factors of the modulus.

    Failure Mode:
        Returns ``Result(success=False, error=...)`` for invalid inputs or when
        no non-trivial factors are found within the trial budget.

    Success Data Keys:
        p: First recovered prime factor.
        q: Second recovered prime factor.
        phi: Euler totient ``(p - 1) * (q - 1)``.

    Args:
        N: RSA modulus.
        e: Public exponent.
        d: Private exponent.
        max_trails: Maximum random attempts used by the current routine.
            The parameter name is preserved for backward compatibility.
        verbose: If True, emit checkpoint logs.

    Returns:
        Result contract containing attack status, outputs, and metadata.
    """
    started = perf_counter()
    log = make_logger("known_d_factorization", verbose)
    log("validate inputs")

    if N <= 1 or e <= 1 or d <= 1:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("N, e, d must be integers greater than 1")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={"tier": TIER, "inputs": {"N": N, "e": e, "d": d}},
            error="N, e, d must be integers greater than 1.",
            elapsed=elapsed_ms,
        )
    
    for _ in range(max_trails):
        a = random.randint(2, N - 1)

        m = e * d - 1
        t = 0
        while m % 2 == 0:
            m //= 2
            t += 1
        
        x = pow(a, m, N)
        for _ in range(t):
            x_next = pow(x, 2, N)
            if x_next == 1 and x != 1 and x != N - 1:
                p = math.gcd(x - 1, N)
                q = math.gcd(x + 1, N)
                if p != 1 and p != N and q != 1 and q != N:
                    elapsed_ms = (perf_counter() - started) * 1000.0
                    log.found("factors found")
                    return Result(
                        success=True,
                        attack=ATTACK_KEY,
                        data={"p": p, "q": q, "phi": (p - 1) * (q - 1)},
                        artifacts={"tier": TIER, "inputs": {"N": N, "e": e, "d": d}},
                        error=None,
                        elapsed=elapsed_ms,
                    )
            x = x_next
    elapsed_ms = (perf_counter() - started) * 1000.0
    log.fail("factors not found after max_trails attempts")
    return Result(
        success=False,
        attack=ATTACK_KEY,
        data={},
        artifacts={"tier": TIER, "inputs": {"N": N, "e": e, "d": d, "max_trails": max_trails}},
        error="Factors not found after max_trails attempts.",
        elapsed=elapsed_ms,
    )
