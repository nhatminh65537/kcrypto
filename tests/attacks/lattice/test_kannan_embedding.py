from __future__ import annotations

from unittest.mock import patch

from kcrypto.attacks.lattice import kannan_embedding

try:
    from sage.all import Matrix, QQ, ZZ
    SAGE_AVAILABLE = True
except ImportError:
    SAGE_AVAILABLE = False


# --- Contract tests (no Sage required) ---

def test_kannan_embedding_no_sage_returns_failure() -> None:
    with patch("kcrypto.bridges.sage.require_sage", side_effect=ImportError("SageMath not found")):
        result = kannan_embedding([[1, 0], [0, 1]], [0, 0])

    assert result.success is False
    assert result.attack == "lattice/kannan_embedding"
    assert result.error is not None


def test_kannan_embedding_failure_has_elapsed() -> None:
    with patch("kcrypto.bridges.sage.require_sage", side_effect=ImportError("no sage")):
        result = kannan_embedding([[1, 0], [0, 1]], [1, 1])

    assert isinstance(result.elapsed, float)
    assert result.elapsed >= 0


# --- Pre-computed Sage tests ---

if SAGE_AVAILABLE:

    def test_kannan_embedding_diagonal_target_at_origin_precomputed() -> None:
        """B=diag(4,4), t=[1,1] → closest=[0,0] (pre-computed)."""
        B = Matrix(ZZ, [[4, 0], [0, 4]])
        result = kannan_embedding(B, [1, 1])

        assert result.success is True
        assert result.attack == "lattice/kannan_embedding"
        assert result.error is None
        assert tuple(result.data["closest_vector"]) == (0, 0)

    def test_kannan_embedding_diagonal_target_far_precomputed() -> None:
        """B=diag(4,4), t=[3,3] → closest=[4,4] (pre-computed)."""
        B = Matrix(ZZ, [[4, 0], [0, 4]])
        result = kannan_embedding(B, [3, 3])

        assert result.success is True
        assert tuple(result.data["closest_vector"]) == (4, 4)

    def test_kannan_embedding_non_diagonal_basis_precomputed() -> None:
        """B=[[2,1],[0,3]], t=[5,5] → closest=[4,5] (pre-computed)."""
        B = Matrix(ZZ, [[2, 1], [0, 3]])
        result = kannan_embedding(B, [5, 5])

        assert result.success is True
        assert tuple(result.data["closest_vector"]) == (4, 5)

    def test_kannan_embedding_3d_lattice_precomputed() -> None:
        """B=diag(4,4,4), t=[1,2,3] → closest=[0,0,4] (pre-computed)."""
        B = Matrix(ZZ, [[4, 0, 0], [0, 4, 0], [0, 0, 4]])
        result = kannan_embedding(B, [1, 2, 3])

        assert result.success is True
        assert tuple(result.data["closest_vector"]) == (0, 0, 4)

    def test_kannan_embedding_result_is_lattice_point() -> None:
        """Result must be expressible as an integer linear combination of basis rows."""
        B = Matrix(QQ, [[2, 1], [0, 3]])
        result = kannan_embedding(B, [7, 8])

        assert result.success is True
        v = result.data["closest_vector"]
        coeffs = B.solve_left(v)
        assert all(c in QQ and c.denominator() == 1 for c in coeffs), (
            f"Closest vector {v} is not a lattice point: coefficients {list(coeffs)}"
        )

    def test_kannan_embedding_artifacts_present() -> None:
        B = Matrix(ZZ, [[4, 0], [0, 4]])
        result = kannan_embedding(B, [3, 3])

        assert result.success is True
        assert "W" in result.artifacts
        assert "embedded_matrix" in result.artifacts
        assert "reduced_matrix" in result.artifacts

    def test_kannan_embedding_custom_W() -> None:
        """Custom W parameter should still find the correct closest vector."""
        B = Matrix(ZZ, [[4, 0], [0, 4]])
        result = kannan_embedding(B, [3, 3], W=4)

        assert result.success is True
        assert tuple(result.data["closest_vector"]) == (4, 4)

    def test_kannan_embedding_verbose_does_not_crash() -> None:
        B = Matrix(ZZ, [[2, 1], [0, 3]])
        result = kannan_embedding(B, [5, 5], verbose=True)

        assert result.success is True
