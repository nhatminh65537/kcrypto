"""Generate Sage pre-computed fixtures for lattice attack tests.

Usage:
    sage -python tests/fixtures/scripts/generate_lattice_fixtures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import sage.all as sa
from sage.modules.free_module_integer import IntegerLattice


FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "lattice" / "lattice_expected_values.json"
)


def _as_int_rows(matrix) -> list[list[int]]:
    return [[int(entry) for entry in row] for row in matrix.rows()]


def _as_int_vector(vector_obj) -> list[int]:
    return [int(entry) for entry in vector_obj]


def build_fixture() -> dict[str, object]:
    """Build deterministic expected values from Sage for tests."""
    basis = [[4, 1, 3], [2, 1, 1], [1, 0, 2]]
    target = [6, 3, 2]

    matrix = sa.Matrix(sa.ZZ, basis)
    lattice = IntegerLattice(matrix)
    target_vec = sa.vector(sa.QQ, target)

    lll_reduced = matrix.LLL(delta=0.99, eta=0.501, algorithm="fpLLL:wrapper")
    bkz_reduced = matrix.BKZ(block_size=2, algorithm="fpLLL")

    cvp_exact = lattice.closest_vector(target_vec)
    cvp_babai = lattice.approximate_closest_vector(
        target_vec,
        algorithm="nearest_plane",
        delta=0.99,
    )
    cvp_kannan = lattice.approximate_closest_vector(
        target_vec,
        algorithm="embedding",
        delta=0.99,
    )
    cvp_enum = lattice.approximate_closest_vector(
        target_vec,
        algorithm="rounding_off",
        delta=0.99,
    )

    def _distance_sq(vec_obj) -> int:
        diff = sa.vector(sa.QQ, vec_obj) - target_vec
        return int(diff.dot_product(diff))

    return {
        "basis": basis,
        "target": target,
        "lll": {
            "delta": 0.99,
            "eta": 0.501,
            "algorithm": "fpLLL:wrapper",
            "reduced_basis": _as_int_rows(lll_reduced),
        },
        "bkz": {
            "block_size": 2,
            "algorithm": "fpLLL",
            "reduced_basis": _as_int_rows(bkz_reduced),
        },
        "cvp": {
            "exact": {
                "closest_vector": _as_int_vector(cvp_exact),
                "distance_sq": _distance_sq(cvp_exact),
            },
            "babai_nearest_plane": {
                "closest_vector": _as_int_vector(cvp_babai),
                "distance_sq": _distance_sq(cvp_babai),
            },
            "kannan_embedding": {
                "closest_vector": _as_int_vector(cvp_kannan),
                "distance_sq": _distance_sq(cvp_kannan),
            },
            "rounding_enumeration": {
                "closest_vector": _as_int_vector(cvp_enum),
                "distance_sq": _distance_sq(cvp_enum),
            },
        },
    }


def main() -> None:
    fixture = build_fixture()
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote fixture to {FIXTURE_PATH}")


if __name__ == "__main__":
    main()
