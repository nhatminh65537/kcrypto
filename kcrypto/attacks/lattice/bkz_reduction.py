"""BKZ lattice basis reduction wrapper."""

from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger


def bkz_reduce(
    basis: Any,
    *,
    verbose: bool = False,
    **kwargs: Any,
) -> Result:
    """Reduce a lattice basis using the BKZ algorithm.

    This function wraps the BKZ (Blockwise Korkine-Zolotarev) lattice basis
    reduction algorithm. BKZ is a more powerful lattice reduction technique
    than LLL, with better quality basis reduction at the cost of higher
    computational complexity. BKZ maintains LLL-reduced blocks of specified
    size.

    Args:
        basis: An object with a `.BKZ(**kwargs)` method (e.g., a Sage matrix).
        verbose: If True, print progress checkpoints. Default False.
        **kwargs: Additional parameters passed to the underlying BKZ implementation.
            Common parameters for Sage's BKZ include:
            - block_size (int): Size of the blocks to reduce (default 10).
            - delta (float): LLL delta parameter in (0.25, 1) (default 0.99).
            - eta (float): LLL eta parameter in (0.5, 1) (default 0.51).
            - strategies (str): Tour strategy ("default", "strong", etc.).
            See Sage documentation for details on parameter effects.

    Returns:
        Result with success=True and data["reduced_basis"] if reduction succeeds.
        Result with success=False and error message on failure (invalid input,
        parameter out of range, method not found, timeout, etc.).

    Raises:
        Nothing. All failures are encoded as Result(success=False, error=...).

    Example:
        >>> from sage.all import Matrix, ZZ
        >>> B = Matrix(ZZ, [[15, 0, 0], [0, 30, 0], [0, 0, 60]])
        >>> result = bkz_reduce(B, block_size=2)
        >>> if result.success:
        ...     print(result.data["reduced_basis"])
    """
    log = make_logger("lattice/bkz_reduction", verbose)
    start = time.time()

    try:
        log("Starting BKZ reduction", "step")

        # Check if the basis has the BKZ method
        if not hasattr(basis, "BKZ") or not callable(getattr(basis, "BKZ")):
            error_msg = (
                f"Basis object missing BKZ method. "
                f"Expected object with .BKZ(**kwargs) method, got {type(basis).__name__}"
            )
            log(error_msg, "fail")
            elapsed = (time.time() - start) * 1000
            return Result(
                success=False,
                attack="lattice/bkz_reduction",
                data={},
                artifacts={},
                error=error_msg,
                elapsed=elapsed,
            )

        # Call the BKZ reduction
        log(f"Calling BKZ with parameters: {kwargs}", "step")
        reduced = basis.BKZ(**kwargs)
        log("BKZ reduction completed successfully", "found")

        elapsed = (time.time() - start) * 1000
        return Result(
            success=True,
            attack="lattice/bkz_reduction",
            data={"reduced_basis": reduced},
            artifacts={"input_basis": basis, "kwargs": kwargs},
            error=None,
            elapsed=elapsed,
        )

    except (TypeError, ValueError, AttributeError) as e:
        # Catch common parameter validation errors from Sage
        error_msg = f"BKZ reduction failed: {type(e).__name__}: {str(e)}"
        log(error_msg, "fail")
        elapsed = (time.time() - start) * 1000
        return Result(
            success=False,
            attack="lattice/bkz_reduction",
            data={},
            artifacts={},
            error=error_msg,
            elapsed=elapsed,
        )
    except Exception as e:
        # Catch unexpected errors (e.g., timeout, memory issues)
        error_msg = f"Unexpected error during BKZ reduction: {type(e).__name__}: {str(e)}"
        log(error_msg, "fail")
        elapsed = (time.time() - start) * 1000
        return Result(
            success=False,
            attack="lattice/bkz_reduction",
            data={},
            artifacts={},
            error=error_msg,
            elapsed=elapsed,
        )
