"""BKZ lattice basis reduction wrapper."""

from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "lattice/bkz_reduction"


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


def bkz_reduce(
    basis: Any,
    *,
    verbose: bool = False,
    **kwargs: Any,
) -> Result:
    """Reduce a lattice basis using the BKZ algorithm.

    Wraps the BKZ (Blockwise Korkine-Zolotarev) lattice basis reduction
    algorithm. BKZ produces higher quality reduction than LLL at greater
    computational cost by maintaining LLL-reduced blocks of specified size.

    Args:
        basis: An object with a `.BKZ(**kwargs)` method (e.g., a Sage matrix).
        verbose: If True, print progress checkpoints. Default False.
        **kwargs: Additional parameters passed to the underlying BKZ implementation.
            Common parameters for Sage's BKZ include:
            - block_size (int): Size of the blocks to reduce (default 10).
            - delta (float): LLL delta parameter in (0.25, 1) (default 0.99).
            - eta (float): LLL eta parameter in (0.5, 1) (default 0.51).
            - strategies (str): Tour strategy ("default", "strong", etc.).

    Returns:
        Result with success=True and data["reduced_basis"] if reduction succeeds.
        Result with success=False and error message on failure.

    Raises:
        Nothing. All failures are encoded as Result(success=False, error=...).

    Example:
        >>> from sage.all import Matrix, ZZ
        >>> B = Matrix(ZZ, [[15, 0, 0], [0, 30, 0], [0, 0, 60]])
        >>> result = bkz_reduce(B, block_size=2)
        >>> if result.success:
        ...     print(result.data["reduced_basis"])
    """
    log = make_logger(_ATTACK, verbose)
    start = time.time()

    try:
        log("Starting BKZ reduction", "step")

        if not hasattr(basis, "BKZ") or not callable(getattr(basis, "BKZ")):
            msg = (
                f"Basis object missing BKZ method. "
                f"Expected object with .BKZ(**kwargs) method, got {type(basis).__name__}"
            )
            log(msg, "fail")
            return _fail(msg, start)

        log(f"Calling BKZ with parameters: {kwargs}", "step")
        reduced = basis.BKZ(**kwargs)
        log("BKZ reduction completed successfully", "found")

        return Result(
            success=True,
            attack=_ATTACK,
            data={"reduced_basis": reduced},
            artifacts={"input_basis": basis, "kwargs": kwargs},
            elapsed=(time.time() - start) * 1000,
        )

    except (TypeError, ValueError, AttributeError) as e:
        msg = f"BKZ reduction failed: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
    except Exception as e:
        msg = f"Unexpected error during BKZ reduction: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
