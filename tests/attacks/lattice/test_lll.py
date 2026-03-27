from __future__ import annotations

from kcrypto.attacks.lattice import lll_reduce

# Import Sage for complex tests (skip if unavailable)
try:
    from sage.all import Matrix, ZZ
    SAGE_AVAILABLE = True
except ImportError:
    SAGE_AVAILABLE = False


class _BasisSuccess:
    def __init__(self) -> None:
        self.called_with: dict[str, object] | None = None

    def LLL(self, **kwargs):
        self.called_with = kwargs
        return [[1, 0], [0, 1]]


class _BasisRaises:
    def LLL(self, **kwargs):
        raise ValueError("delta must be in (0.25, 1)")


class _BasisMissingMethod:
    pass


def test_lll_reduce_success_returns_result_with_reduced_basis() -> None:
    basis = _BasisSuccess()

    result = lll_reduce(basis, delta=0.99)

    assert result.success is True
    assert result.attack == "lattice/lll_reduction"
    assert result.data["reduced_basis"] == [[1, 0], [0, 1]]
    assert result.error is None
    assert basis.called_with == {"delta": 0.99}


def test_lll_reduce_failure_returns_result_instead_of_raising() -> None:
    basis = _BasisRaises()

    result = lll_reduce(basis, delta=1.5)

    assert result.success is False
    assert result.attack == "lattice/lll_reduction"
    assert "delta" in (result.error or "")


def test_lll_reduce_edge_basis_without_lll_method() -> None:
    basis = _BasisMissingMethod()

    result = lll_reduce(basis)

    assert result.success is False
    assert result.attack == "lattice/lll_reduction"
    assert "LLL" in (result.error or "")


# Complex test cases with pre-computed Sage matrice outputs
if SAGE_AVAILABLE:

    def test_lll_reduce_3x3_random_matrix_precomputed() -> None:
        """Test LLL reduction on 3x3 random matrix (pre-computed expected output)."""
        B = Matrix(ZZ, [
            [100, 50, 25],
            [50, 100, 30],
            [25, 30, 100]
        ])
        result = lll_reduce(B, verbose=False)

        # Pre-computed expected output
        expected = [(-50, 50, 5), (-25, -70, 70), (25, 30, 100)]

        assert result.success is True
        assert result.attack == "lattice/lll_reduction"
        assert result.error is None
        # Convert Sage vectors to tuples for comparison
        reduced = result.data["reduced_basis"]
        actual = [tuple(row) for row in reduced.rows()] if hasattr(reduced, "rows") else reduced
        assert actual == expected

    def test_lll_reduce_4x4_sequential_matrix_precomputed() -> None:
        """Test LLL reduction on 4x4 sequential matrix (pre-computed)."""
        B = Matrix(ZZ, [
            [10, 20, 30, 40],
            [20, 30, 40, 50],
            [30, 40, 50, 60],
            [40, 50, 60, 70]
        ])
        result = lll_reduce(B, verbose=False)

        # Pre-computed expected output
        expected = [(0, 0, 0, 0), (0, 0, 0, 0), (10, 10, 10, 10), (-10, 0, 10, 20)]

        assert result.success is True
        reduced = result.data["reduced_basis"]
        actual = [tuple(row) for row in reduced.rows()] if hasattr(reduced, "rows") else reduced
        assert actual == expected

    def test_lll_reduce_3x3_large_coefficients_precomputed() -> None:
        """Test LLL reduction on 3x3 matrix with large coefficients (pre-computed)."""
        B = Matrix(ZZ, [
            [1000, 2000, 3000],
            [2000, 5000, 7000],
            [3000, 7000, 12000]
        ])
        result = lll_reduce(B, verbose=False)

        # Pre-computed expected output
        expected = [(0, 1000, 1000), (1000, 0, 1000), (-1000, -1000, 0)]

        assert result.success is True
        reduced = result.data["reduced_basis"]
        actual = [tuple(row) for row in reduced.rows()] if hasattr(reduced, "rows") else reduced
        assert actual == expected

    def test_lll_reduce_with_delta_parameter_precomputed() -> None:
        """Test LLL reduction with delta=0.75 parameter (pre-computed)."""
        B = Matrix(ZZ, [
            [100, 200, 150],
            [200, 500, 300],
            [150, 300, 400]
        ])
        result = lll_reduce(B, delta=0.75, verbose=False)

        # Pre-computed expected output with delta=0.75
        expected = [(0, 100, 0), (-50, 0, 100), (150, 0, 50)]

        assert result.success is True
        reduced = result.data["reduced_basis"]
        actual = [tuple(row) for row in reduced.rows()] if hasattr(reduced, "rows") else reduced
        assert actual == expected

    def test_lll_reduce_simple_2d_lattice() -> None:
        """Test LLL reduction on simple 2D lattice."""
        B = Matrix(ZZ, [[1, 1], [1, 0]])
        result = lll_reduce(B, verbose=False)

        assert result.success is True
        assert result.attack == "lattice/lll_reduction"
        assert result.error is None
        assert "reduced_basis" in result.data
        assert result.data["reduced_basis"] is not None
