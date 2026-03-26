"""Tests for Result and Finding contracts."""

from __future__ import annotations

import pytest

from kcrypto.core.contracts import Finding, Result


def test_result_getitem_and_getattr_read_data_values() -> None:
    result = Result(success=True, attack="wiener", data={"d": 1337})

    assert result["d"] == 1337
    assert result.d == 1337


def test_result_missing_attribute_raises_attribute_error() -> None:
    result = Result(success=True, attack="wiener", data={"d": 1337})

    with pytest.raises(AttributeError):
        _ = result.not_present


def test_result_repr_success_includes_attack_and_data() -> None:
    result = Result(success=True, attack="wiener", data={"d": 1337}, elapsed=12.4)

    text = repr(result)

    assert "Result(" in text
    assert "wiener" in text
    assert "d" in text


def test_result_repr_failure_includes_error() -> None:
    result = Result(
        success=False,
        attack="wiener",
        error="no convergent satisfied constraints",
        elapsed=2.0,
    )

    text = repr(result)

    assert "Result(" in text
    assert "error" in text
    assert "no convergent" in text


def test_result_repr_html_contains_attack_and_status() -> None:
    result = Result(success=True, attack="wiener", data={"d": 1337}, elapsed=12.4)

    html = result._repr_html_()

    assert "<" in html
    assert "wiener" in html
    assert "success" in html.lower()


def test_finding_fields_match_contract() -> None:
    finding = Finding(
        name="wiener_candidate",
        confidence=0.8,
        reason="d appears too small for N",
        suggested="wiener",
        params={"threshold": 0.25},
    )

    assert finding.name == "wiener_candidate"
    assert finding.confidence == 0.8
    assert finding.reason.startswith("d appears")
    assert finding.suggested == "wiener"
    assert finding.params["threshold"] == 0.25


def test_finding_repr_is_notebook_friendly() -> None:
    finding = Finding(
        name="wiener_candidate",
        confidence=0.8,
        reason="d appears too small for N",
        suggested="wiener",
        params={"threshold": 0.25},
    )

    text = repr(finding)

    assert text.startswith("Finding(wiener_candidate, confidence=0.80)")
    assert "  reason = d appears too small for N" in text
    assert "  suggested = wiener" in text


def test_finding_repr_html_contains_name_and_confidence() -> None:
    finding = Finding(
        name="wiener_candidate",
        confidence=0.8,
        reason="d appears too small for N",
        suggested="wiener",
        params={"threshold": 0.25},
    )

    html = finding._repr_html_()

    assert "<" in html
    assert "wiener_candidate" in html
    assert "0.800" in html
