"""Shared fixture helpers for lattice attack tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_lattice_expected_values() -> dict[str, Any]:
    """Load pre-computed Sage expected values for lattice tests."""
    fixture_path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "lattice"
        / "lattice_expected_values.json"
    )
    return json.loads(fixture_path.read_text(encoding="utf-8"))
