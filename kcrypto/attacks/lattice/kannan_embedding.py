"""Kannan's embedding technique for CVP via LLL reduction."""

from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "lattice/kannan_embedding"


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


def kannan_embedding(
    basis: Any,
    target: Any,
    W: Any = None,
    *,
    verbose: bool = False,
) -> Result:
    """Solve CVP via Kannan's embedding technique.

    Embeds the CVP instance into a higher-dimensional lattice and applies LLL
    reduction. A row with last coordinate ±W in the reduced basis reveals the
    closest vector.

    Args:
        basis: A 2D sequence or Sage matrix (n×n) representing the lattice basis.
        target: A sequence or Sage vector of length n representing the target point.
        W: Embedding weight. If None, defaults to 1. A larger W biases LLL toward
            finding the target row. Typically set to the lattice determinant or the
            expected distance.
        verbose: If True, print progress checkpoints. Default False.

    Returns:
        Result with success=True and data["closest_vector"] on success.
        Result with success=False and error message when no embedding row is found
        or on failure.

    Raises:
        Nothing. All failures are encoded as Result(success=False, error=...).

    Example:
        >>> from sage.all import Matrix, QQ
        >>> B = Matrix(QQ, [[2, 1], [0, 3]])
        >>> result = kannan_embedding(B, [5, 5])
        >>> if result.success:
        ...     print(result.data["closest_vector"])
    """
    log = make_logger(_ATTACK, verbose)
    start = time.time()

    try:
        from kcrypto.bridges.sage import require_sage
        sage = require_sage()

        if W is None:
            W = 1

        log("Building embedding matrix", "step")
        B = sage.Matrix(sage.QQ, basis)
        n = B.nrows()
        top = sage.block_matrix([[B, sage.Matrix(sage.QQ, n, 1)]], subdivide=False)
        bottom = sage.Matrix(sage.QQ, [list(target) + [W]])
        M = sage.block_matrix([[top], [bottom]], subdivide=False)

        log("Running LLL on embedded matrix", "step")
        L = M.LLL()

        target_vec = sage.vector(sage.QQ, target)
        for row in L:
            if row[-1] == W:
                closest = target_vec - sage.vector(sage.QQ, row[:-1])
                log(f"Found closest vector via +W row: {closest}", "found")
                return Result(
                    success=True,
                    attack=_ATTACK,
                    data={"closest_vector": closest},
                    artifacts={"W": W, "embedded_matrix": M, "reduced_matrix": L},
                    elapsed=(time.time() - start) * 1000,
                )
            if row[-1] == -W:
                closest = target_vec + sage.vector(sage.QQ, row[:-1])
                log(f"Found closest vector via -W row: {closest}", "found")
                return Result(
                    success=True,
                    attack=_ATTACK,
                    data={"closest_vector": closest},
                    artifacts={"W": W, "embedded_matrix": M, "reduced_matrix": L},
                    elapsed=(time.time() - start) * 1000,
                )

        msg = "LLL did not produce an embedding row with last coordinate ±W; try a different W"
        log(msg, "fail")
        return _fail(msg, start)

    except ImportError as e:
        msg = str(e)
        log(msg, "fail")
        return _fail(msg, start)
    except (TypeError, ValueError, AttributeError) as e:
        msg = f"Kannan embedding failed: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
    except Exception as e:
        msg = f"Unexpected error during Kannan embedding: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
