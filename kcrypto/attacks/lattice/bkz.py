"""BKZ lattice reduction attack wrapper (Tier 1).

This module wraps SageMath's BKZ reduction and exposes the output via
kcrypto's ``Result`` contract.
"""

from __future__ import annotations

from time import perf_counter
from typing import Sequence

from kcrypto.bridges.sage import require_sage
from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger


TIER = "T1"


def bkz_reduce(
    basis: Sequence[Sequence[int]],
    *,
    block_size: int = 10,
    delta: float | None = None,
    algorithm: str = "fpLLL",
    verbose: bool = False,
) -> Result:
    """Reduce an integer lattice basis using SageMath BKZ.

    Tier:
        T1 (pure function).

    Applicability:
        Use when stronger reduction than LLL is needed, typically as a preprocessing
        step for lattice attacks that benefit from short vectors.

    Args:
        basis: Input basis as row vectors.
        block_size: BKZ block size (trade-off between runtime and quality).
        delta: Optional LLL parameter used inside BKZ in Sage.
        algorithm: Sage BKZ backend selector.
        verbose: If True, emit logger checkpoints.

    Returns:
        Result: ``success=True`` with ``data['reduced_basis']`` on success,
        or ``success=False`` with an actionable error string.

    Failure Mode:
        Returns ``Result(success=False, error=...)`` for invalid parameters,
        missing optional dependency, or Sage runtime errors.
    """
    log = make_logger("lattice/bkz_reduction", verbose)
    started = perf_counter()

    if not basis:
        log.fail("input basis is empty")
        return Result(
            success=False,
            attack="lattice/bkz_reduction",
            error="basis must not be empty",
            elapsed=(perf_counter() - started) * 1000,
        )

    if block_size < 2:
        log.fail("invalid block size")
        return Result(
            success=False,
            attack="lattice/bkz_reduction",
            error="block_size must be >= 2",
            data={"block_size": block_size},
            elapsed=(perf_counter() - started) * 1000,
        )

    try:
        sage = require_sage()
        matrix = sage.Matrix(sage.ZZ, [list(row) for row in basis])
        kwargs: dict[str, object] = {
            "algorithm": algorithm,
            "block_size": block_size,
        }
        if delta is not None:
            kwargs["delta"] = delta
        log("running Sage BKZ")
        reduced = matrix.BKZ(**kwargs)
    except Exception as exc:  # pragma: no cover - exercised by bridge tests
        log.fail(f"BKZ failed: {exc}")
        return Result(
            success=False,
            attack="lattice/bkz_reduction",
            error=str(exc),
            data={
                "block_size": block_size,
                "delta": delta,
                "algorithm": algorithm,
            },
            elapsed=(perf_counter() - started) * 1000,
        )

    reduced_basis = [list(map(int, row)) for row in reduced.rows()]
    log.found("BKZ reduction completed")
    return Result(
        success=True,
        attack="lattice/bkz_reduction",
        data={
            "reduced_basis": reduced_basis,
            "dimension": int(matrix.nrows()),
            "rank": int(matrix.rank()),
            "block_size": block_size,
            "delta": delta,
            "algorithm": algorithm,
        },
        elapsed=(perf_counter() - started) * 1000,
    )
