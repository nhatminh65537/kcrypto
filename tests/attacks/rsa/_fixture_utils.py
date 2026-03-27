"""Shared fixture helpers for RSA attack tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "rsa"
    / "sage_precomputed_rsa_attacks.json"
)


def load_rsa_cases() -> dict[str, Any]:
    """Load all RSA fixture cases from the precomputed Sage JSON file."""
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))["cases"]


def load_rsa_case(case_name: str) -> dict[str, Any]:
    """Load a single RSA fixture case by name."""
    return load_rsa_cases()[case_name]


def assert_modulus_size(case: dict[str, Any]) -> None:
    """Assert fixture modulus is at least 1024 bits."""
    assert int(case["inputs"]["N"]).bit_length() >= 1024
