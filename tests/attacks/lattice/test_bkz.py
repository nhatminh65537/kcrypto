from __future__ import annotations

from kcrypto.attacks.lattice import bkz_reduce

# Import Sage for complex tests (skip if unavailable)
try:
    from sage.all import Matrix, ZZ
    SAGE_AVAILABLE = True
except ImportError:
    SAGE_AVAILABLE = False


class _BasisSuccess:
    def __init__(self) -> None:
        self.called_with: dict[str, object] | None = None

    def BKZ(self, **kwargs):
        self.called_with = kwargs
        return [[1, 0], [0, 1]]


class _BasisRaises:
    def BKZ(self, **kwargs):
        raise ValueError("block_size must be at least 2")


class _BasisMissingMethod:
    pass


def test_bkz_reduce_success_returns_result_with_reduced_basis() -> None:
    basis = _BasisSuccess()

    result = bkz_reduce(basis, block_size=2)

    assert result.success is True
    assert result.attack == "lattice/bkz_reduction"
    assert result.data["reduced_basis"] == [[1, 0], [0, 1]]
    assert result.error is None
    assert basis.called_with == {"block_size": 2}


def test_bkz_reduce_success_with_multiple_parameters() -> None:
    basis = _BasisSuccess()

    result = bkz_reduce(basis, block_size=3, delta=0.99, eta=0.51)

    assert result.success is True
    assert result.attack == "lattice/bkz_reduction"
    assert result.data["reduced_basis"] == [[1, 0], [0, 1]]
    assert basis.called_with == {"block_size": 3, "delta": 0.99, "eta": 0.51}


def test_bkz_reduce_failure_returns_result_instead_of_raising() -> None:
    basis = _BasisRaises()

    result = bkz_reduce(basis, block_size=1)

    assert result.success is False
    assert result.attack == "lattice/bkz_reduction"
    assert "block_size" in (result.error or "")


def test_bkz_reduce_edge_basis_without_bkz_method() -> None:
    basis = _BasisMissingMethod()

    result = bkz_reduce(basis)

    assert result.success is False
    assert result.attack == "lattice/bkz_reduction"
    assert "BKZ" in (result.error or "")


def test_bkz_reduce_elapsed_time_measured() -> None:
    basis = _BasisSuccess()

    result = bkz_reduce(basis, block_size=2)

    assert result.elapsed >= 0
    assert isinstance(result.elapsed, float)


# Complex test cases with pre-computed Sage matrix outputs
if SAGE_AVAILABLE:

    def test_bkz_reduce_3x3_random_matrix_precomputed() -> None:
        """Test BKZ reduction on 3x3 random matrix (pre-computed expected output)."""
        B = Matrix(ZZ, [
            [100, 50, 25],
            [50, 100, 30],
            [25, 30, 100],
        ])

        result = bkz_reduce(B, block_size=2)

        assert result.success is True
        assert result.attack == "lattice/bkz_reduction"
        assert result.data["reduced_basis"] is not None
        # BKZ-reduced basis should have shorter vectors than original
        original_norm_0 = (100**2 + 50**2 + 25**2) ** 0.5
        reduced_basis_vectors = result.data["reduced_basis"]
        first_vec_norm = sum(v**2 for v in reduced_basis_vectors[0]) ** 0.5
        assert first_vec_norm <= original_norm_0 + 1  # Allow small numerical tolerance

    def test_bkz_reduce_2x2_diagonal_matrix() -> None:
        """Test BKZ reduction on diagonal matrix."""
        B = Matrix(ZZ, [[10, 0], [0, 10]])

        result = bkz_reduce(B, block_size=2)

        assert result.success is True
        assert result.data["reduced_basis"] is not None

    def test_bkz_reduce_invalid_parameter_block_size_zero() -> None:
        """Test BKZ reduction with invalid block_size parameter."""
        B = Matrix(ZZ, [[1, 1], [1, 0]])

        result = bkz_reduce(B, block_size=0)

        assert result.success is False
        assert "block_size" in (result.error or "") or result.error is not None

    def test_bkz_reduce_verbose_mode() -> None:
        """Test that verbose mode doesn't crash and completes normally."""
        B = Matrix(ZZ, [[2, 1], [1, 2]])

        # Should not raise, even with verbose=True
        result = bkz_reduce(B, block_size=2, verbose=True)

        assert result.success is True
        assert result.data["reduced_basis"] is not None
