from kcrypto.bridges.sage import sage

# TODO: add logger, follow contract design, add docstring (describe input, output, and failure modes, search web for BKZ parameters and their effects, etc.), add tests, catch exceptions

def bkz(B, **kwargs):
    """Wrapper for Sage's BKZ lattice reduction algorithm."""
    R = B.BKZ(**kwargs)
    return R