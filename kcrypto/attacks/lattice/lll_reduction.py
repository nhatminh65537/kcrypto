"""LLL lattice basis reduction wrapper."""

from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger


def lll_reduce(
    basis: Any,
    *,
    verbose: bool = False,
    **kwargs: Any,
) -> Result:
    """Reduce a lattice basis using the LLL algorithm.

    This function wraps the LLL (Lenstra–Lenstra–Lovász) lattice basis reduction
    algorithm. LLL reduces a lattice basis to a "short" and "nearly orthogonal"
    basis, which is useful in cryptanalysis and lattice-based problem solving.

    Args:
        basis: An object with a `.LLL(**kwargs)` method (e.g., a Sage matrix).
        verbose: If True, print progress checkpoints. Default False.
        **kwargs: Additional parameters passed to the underlying LLL implementation
            (e.g., delta=0.99, eta=0.51 for Sage's LLL). See Sage documentation for
            details on parameter effects.

    Returns:
        Result with success=True and data["reduced_basis"] if reduction succeeds.
        Result with success=False and error message on failure (invalid input,
        parameter out of range, method not found, etc.).

    Raises:
        Nothing. All failures are encoded as Result(success=False, error=...).

    Example:
        >>> from sage.all import Matrix, ZZ
        >>> B = Matrix(ZZ, [[1, 1], [1, 0]])
        >>> result = lll_reduce(B)
        >>> if result.success:
        ...     print(result.data["reduced_basis"])
    """
    log = make_logger("lattice/lll_reduction", verbose)
    start = time.time()

    try:
        log("Starting LLL reduction", "step")

        # Check if the basis has the LLL method
        if not hasattr(basis, "LLL") or not callable(getattr(basis, "LLL")):
            error_msg = (
                f"Basis object missing LLL method. "
                f"Expected object with .LLL(**kwargs) method, got {type(basis).__name__}"
            )
            log(error_msg, "fail")
            elapsed = (time.time() - start) * 1000
            return Result(
                success=False,
                attack="lattice/lll_reduction",
                data={},
                artifacts={},
                error=error_msg,
                elapsed=elapsed,
            )

        # Call the LLL reduction
        log(f"Calling LLL with parameters: {kwargs}", "step")
        reduced = basis.LLL(**kwargs)
        log("LLL reduction completed successfully", "found")

        elapsed = (time.time() - start) * 1000
        return Result(
            success=True,
            attack="lattice/lll_reduction",
            data={"reduced_basis": reduced},
            artifacts={"input_basis": basis, "kwargs": kwargs},
            error=None,
            elapsed=elapsed,
        )

    except (TypeError, ValueError, AttributeError) as e:
        # Catch common parameter validation errors from Sage
        error_msg = f"LLL reduction failed: {type(e).__name__}: {str(e)}"
        log(error_msg, "fail")
        elapsed = (time.time() - start) * 1000
        return Result(
            success=False,
            attack="lattice/lll_reduction",
            data={},
            artifacts={},
            error=error_msg,
            elapsed=elapsed,
        )
    except Exception as e:
        # Catch unexpected errors
        error_msg = f"Unexpected error during LLL reduction: {type(e).__name__}: {str(e)}"
        log(error_msg, "fail")
        elapsed = (time.time() - start) * 1000
        return Result(
            success=False,
            attack="lattice/lll_reduction",
            data={},
            artifacts={},
            error=error_msg,
            elapsed=elapsed,
        )
