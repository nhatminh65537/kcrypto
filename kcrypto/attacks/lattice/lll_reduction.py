"""LLL lattice basis reduction wrapper."""

from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "lattice/lll_reduction"


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


def lll_reduce(
    basis: Any,
    *,
    verbose: bool = False,
    **kwargs: Any,
) -> Result:
    """Reduce a lattice basis using the LLL algorithm.

    Wraps the LLL (Lenstra–Lenstra–Lovász) lattice basis reduction algorithm.
    LLL reduces a lattice basis to a "short" and "nearly orthogonal" basis,
    which is useful in cryptanalysis and lattice-based problem solving.

    Args:
        basis: An object with a `.LLL(**kwargs)` method (e.g., a Sage matrix).
        verbose: If True, print progress checkpoints. Default False.
        **kwargs: Additional parameters passed to the underlying LLL implementation
            (e.g., delta=0.99, eta=0.51 for Sage's LLL).

    Returns:
        Result with success=True and data["reduced_basis"] if reduction succeeds.
        Result with success=False and error message on failure.

    Raises:
        Nothing. All failures are encoded as Result(success=False, error=...).

    Example:
        >>> from sage.all import Matrix, ZZ
        >>> B = Matrix(ZZ, [[1, 1], [1, 0]])
        >>> result = lll_reduce(B)
        >>> if result.success:
        ...     print(result.data["reduced_basis"])
    """
    log = make_logger(_ATTACK, verbose)
    start = time.time()

    try:
        log("Starting LLL reduction", "step")

        if not hasattr(basis, "LLL") or not callable(getattr(basis, "LLL")):
            msg = (
                f"Basis object missing LLL method. "
                f"Expected object with .LLL(**kwargs) method, got {type(basis).__name__}"
            )
            log(msg, "fail")
            return _fail(msg, start)

        log(f"Calling LLL with parameters: {kwargs}", "step")
        reduced = basis.LLL(**kwargs)
        log("LLL reduction completed successfully", "found")

        return Result(
            success=True,
            attack=_ATTACK,
            data={"reduced_basis": reduced},
            artifacts={"input_basis": basis, "kwargs": kwargs},
            elapsed=(time.time() - start) * 1000,
        )

    except (TypeError, ValueError, AttributeError) as e:
        msg = f"LLL reduction failed: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
    except Exception as e:
        msg = f"Unexpected error during LLL reduction: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
