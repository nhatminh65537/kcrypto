"""LLL lattice reduction attack wrapper (Tier 1).

This module wraps SageMath's integer lattice LLL reduction routine and returns
results using kcrypto's ``Result`` contract.
"""

from __future__ import annotations

from time import perf_counter
from typing import Sequence

from kcrypto.bridges.sage import require_sage
from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger


TIER = "T1"


def lll_reduce(
    basis: Sequence[Sequence[int]],
    *,
    delta: float = 0.99,
    eta: float = 0.501,
    algorithm: str = "fpLLL:wrapper",
    verbose: bool = False,
) -> Result:
    """Reduce an integer lattice basis using SageMath LLL.

    Tier:
        T1 (pure function).

    Applicability:
        Use when an integer basis should be reduced to a shorter, near-orthogonal
        basis before further lattice cryptanalysis steps.

    Args:
        basis: Input basis as row vectors.
        delta: LLL Lovasz parameter in ``(0.25, 1]``.
        eta: Size-reduction parameter in ``[0.5, delta)``.
        algorithm: Sage LLL backend selector.
        verbose: If True, emit logger checkpoints.

    Returns:
        Result: ``success=True`` with ``data['reduced_basis']`` and metadata fields,
        or ``success=False`` with ``error`` describing why reduction failed.

    Failure Mode:
        Returns ``Result(success=False, error=...)`` for invalid input, missing
        optional dependency, or Sage runtime errors.
    """
    log = make_logger("lattice/lll_reduction", verbose)
    started = perf_counter()

    if not basis:
        log.fail("input basis is empty")
        return Result(
            success=False,
            attack="lattice/lll_reduction",
            error="basis must not be empty",
            elapsed=(perf_counter() - started) * 1000,
        )

    try:
        sage = require_sage()
        matrix = sage.Matrix(sage.ZZ, [list(row) for row in basis])
        log("running Sage LLL")
        reduced = matrix.LLL(delta=delta, eta=eta, algorithm=algorithm)
    except Exception as exc:  # pragma: no cover - exercised by bridge tests
        log.fail(f"LLL failed: {exc}")
        return Result(
            success=False,
            attack="lattice/lll_reduction",
            error=str(exc),
            data={"delta": delta, "eta": eta, "algorithm": algorithm},
            elapsed=(perf_counter() - started) * 1000,
        )

    reduced_basis = [list(map(int, row)) for row in reduced.rows()]
    log.found("LLL reduction completed")
    return Result(
        success=True,
        attack="lattice/lll_reduction",
        data={
            "reduced_basis": reduced_basis,
            "dimension": int(matrix.nrows()),
            "rank": int(matrix.rank()),
            "delta": float(delta),
            "eta": float(eta),
            "algorithm": algorithm,
        },
        elapsed=(perf_counter() - started) * 1000,
    )
