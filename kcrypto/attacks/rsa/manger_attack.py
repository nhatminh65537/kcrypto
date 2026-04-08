"""Manger's chosen-ciphertext attack on OAEP-like padding."""

from __future__ import annotations

import time
from collections.abc import Callable

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "rsa/manger_attack"


class MangerAttack:
    """Recover RSA plaintext via Manger's padding oracle attack (Tier 3).

    Manger's attack (2001) recovers an RSA-OAEP plaintext given a oracle that
    reveals whether the first byte of the decrypted ciphertext is 0x00.
    Requires O(log n) oracle queries.

    Args:
        c: Ciphertext to decrypt (integer).
        n: RSA modulus.
        e: RSA public exponent.
        oracle: Callable that takes an integer ciphertext and returns True when the
            first byte of the corresponding decryption is 0x00 (i.e., decryption < B).
        B: Padding bound. If None, defaults to 2^(n.bit_length() - 8).
        verbose: If True, print progress checkpoints. Default False.

    Example:
        >>> attack = MangerAttack(c, n, e, oracle)
        >>> result = attack.run()
        >>> if result.success:
        ...     print(result.data["plaintext"])
    """

    def __init__(
        self,
        c: int,
        n: int,
        e: int,
        oracle: Callable[[int], bool],
        *,
        B: int | None = None,
        verbose: bool = False,
    ) -> None:
        self.c = c
        self.n = n
        self.e = e
        self.oracle = oracle
        self.B = B if B is not None else 2 ** (n.bit_length() - 8)
        self.verbose = verbose

    def run(self) -> Result:
        """Execute the Manger attack and return the recovered plaintext.

        Returns:
            Result with success=True and data["plaintext"] on success.
            Result with success=False and error message on failure.
        """
        log = make_logger(_ATTACK, self.verbose)
        start = time.time()
        queries = 0

        def query(ct: int) -> bool:
            nonlocal queries
            queries += 1
            return self.oracle(ct)

        try:
            c, n, e, B = self.c, self.n, self.e, self.B

            # Step 1: find f1 = 2^t such that f1*m ∈ [B, 2B)
            log("Step 1: finding f1", "step")
            f1 = 2
            while query(pow(f1, e, n) * c % n):
                f1 *= 2
            log(f"Found f1 = {f1}", "found")

            # Step 2: find f2 such that f2*m ∈ [n, n+B)
            log("Step 2: finding f2", "step")
            f2 = ((n + B) // B) * (f1 // 2)
            while not query(pow(f2, e, n) * c % n):
                f2 += f1 // 2
            log(f"Found f2 = {f2}", "found")

            lbound = -(-n // f2)
            rbound = (n + B - 1) // f2

            # Step 3: binary search to narrow interval to a single value
            log("Step 3: binary search", "step")
            while lbound < rbound:
                ft = 2 * B // (rbound - lbound)
                i = ft * lbound // n
                f3 = -(-i * n // lbound)

                if query(pow(f3, e, n) * c % n):
                    rbound = (i * n + B - 1) // f3
                else:
                    lbound = -(-(i * n + B) // f3)

            plaintext = lbound
            log(f"Recovered plaintext in {queries} queries", "found")

            return Result(
                success=True,
                attack=_ATTACK,
                data={"plaintext": plaintext},
                artifacts={"queries": queries, "f1": f1, "f2": f2},
                elapsed=(time.time() - start) * 1000,
            )

        except Exception as e:
            msg = f"Manger attack failed: {type(e).__name__}: {e}"
            log(msg, "fail")
            return Result(
                success=False,
                attack=_ATTACK,
                error=msg,
                artifacts={"queries": queries},
                elapsed=(time.time() - start) * 1000,
            )
