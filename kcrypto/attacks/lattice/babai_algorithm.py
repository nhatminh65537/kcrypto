"""Babai's nearest plane algorithm for solving CVP."""

from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "lattice/babai_cvp"


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


def babai_cvp(
    basis: Any,
    target: Any,
    *,
    verbose: bool = False,
) -> Result:
    """Find the closest lattice vector to a target using Babai's nearest plane algorithm.

    Uses Gram-Schmidt orthogonalization to iteratively project the target onto
    each basis vector, rounding coefficients to find the nearest lattice point.
    Works well when the lattice basis is already reasonably reduced (e.g., LLL-reduced).

    Args:
        basis: A 2D sequence or Sage matrix representing the lattice basis (n×n).
        target: A sequence or Sage vector of length n representing the target point.
        verbose: If True, print progress checkpoints. Default False.

    Returns:
        Result with success=True and data["closest_vector"] on success.
        Result with success=False and error message on failure.

    Raises:
        Nothing. All failures are encoded as Result(success=False, error=...).

    Example:
        >>> from sage.all import Matrix, QQ, vector
        >>> B = Matrix(QQ, [[2, 1], [0, 3]])
        >>> result = babai_cvp(B, [5, 5])
        >>> if result.success:
        ...     print(result.data["closest_vector"])
    """
    log = make_logger(_ATTACK, verbose)
    start = time.time()

    try:
        from kcrypto.bridges.sage import require_sage
        sage = require_sage()

        log("Building QQ matrix from basis", "step")
        B = sage.Matrix(sage.QQ, basis)
        G, _ = B.gram_schmidt()
        t = sage.vector(sage.QQ, target)
        t_orig = sage.vector(sage.QQ, target)

        log("Running nearest-plane projection", "step")
        for i in range(B.nrows() - 1, -1, -1):
            c = round((t * G[i]) / (G[i] * G[i]))
            t -= c * B[i]

        closest = t_orig - t
        log(f"Found closest vector: {closest}", "found")

        return Result(
            success=True,
            attack=_ATTACK,
            data={"closest_vector": closest},
            artifacts={"gram_schmidt": G},
            elapsed=(time.time() - start) * 1000,
        )

    except ImportError as e:
        msg = str(e)
        log(msg, "fail")
        return _fail(msg, start)
    except (TypeError, ValueError, AttributeError) as e:
        msg = f"Babai CVP failed: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
    except Exception as e:
        msg = f"Unexpected error during Babai CVP: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
