"""Factor RSA modulus with Fermat decomposition (Tier 1)."""

from __future__ import annotations

import math
from time import perf_counter

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger


TIER = "T1"
ATTACK_KEY = "rsa/fermat_factorization"


def fermat_factorization(
    N: int,
    *,
    max_iterations: int | None = None,
    verbose: bool = False,
) -> Result:
    """Factor an odd modulus ``N`` using Fermat's difference-of-squares method.

    Tier:
        T1 (pure function).

    Applicability:
        Most effective when the prime factors are close, meaning ``|p - q|`` is
        relatively small.

    Failure Mode:
        Returns ``Result(success=False, error=...)`` for invalid inputs, when no
        square decomposition is found under the iteration bound, or when only
        trivial factors are produced.

    Success Data Keys:
        p: First recovered prime factor.
        q: Second recovered prime factor.
        iterations: Number of loop iterations needed before recovery.

    Args:
        N: RSA modulus to factor.
        max_iterations: Optional upper bound on search iterations.
        verbose: If True, emit checkpoint logs.

    Returns:
        Result contract containing attack status, outputs, and metadata.
    """
    started = perf_counter()
    log = make_logger("fermat_factorization", verbose)
    log("validate inputs")

    if not isinstance(N, int) or N <= 1 or (N % 2 == 0):
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("N must be an odd integer greater than 1")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={
                "tier": TIER,
                "inputs": {"N": N, "max_iterations": max_iterations},
            },
            error="N must be an odd integer greater than 1.",
            elapsed=elapsed_ms,
        )

    if max_iterations is not None and max_iterations <= 0:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("max_iterations must be positive when provided")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={
                "tier": TIER,
                "inputs": {"N": N, "max_iterations": max_iterations},
            },
            error="max_iterations must be positive when provided.",
            elapsed=elapsed_ms,
        )

    if max_iterations is None:
        max_iterations = 10_000  # Default safety bound for iteration count.

    a = math.isqrt(N)
    if a * a < N:
        a += 1

    b2 = a * a - N
    iterations_completed = 0
    for iterations in range(max_iterations):
        b = math.isqrt(b2)
        if b * b == b2:
            iterations_completed = iterations + 1
            break
        a += 1
        b2 = a * a - N
        iterations_completed = iterations + 1
    else:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("Fermat factorization failed to find a solution within max_iterations")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={
                "tier": TIER,
                "inputs": {"N": N, "max_iterations": max_iterations},
                "iterations_completed": iterations_completed,
            },
            error="Fermat factorization failed to find a solution within max_iterations.",
            elapsed=elapsed_ms,
        )

    p = a + b
    q = a - b

    if p <= 1 or q <= 1:
        elapsed_ms = (perf_counter() - started) * 1000.0
        log.fail("Fermat factorization found only trivial factors")
        return Result(
            success=False,
            attack=ATTACK_KEY,
            data={},
            artifacts={
                "tier": TIER,
                "inputs": {"N": N, "max_iterations": max_iterations},
                "iterations_completed": iterations_completed,
                "candidate_factors": {"p": p, "q": q},
            },
            error="Fermat factorization found only trivial factors; non-trivial factors were not recovered.",
            elapsed=elapsed_ms,
        )

    elapsed_ms = (perf_counter() - started) * 1000.0
    log.found(f"Fermat factorization found factors in {iterations_completed} iterations")
    return Result(
        success=True,
        attack=ATTACK_KEY,
        data={"p": p, "q": q, "iterations": iterations_completed},
        artifacts={
            "tier": TIER,
            "inputs": {"N": N, "max_iterations": max_iterations},
        },
        elapsed=elapsed_ms,
    )