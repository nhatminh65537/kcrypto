"""Tests for logger contract."""

from __future__ import annotations

from kcrypto.core.logger import make_logger


def test_logger_is_silent_when_verbose_false(capsys) -> None:
    log = make_logger("wiener", verbose=False)

    log("start")
    log.found("recovered d")
    log.fail("constraint not met")
    log.warn("beta may be too small")

    captured = capsys.readouterr()
    assert captured.out == ""


def test_logger_emits_expected_markers_when_verbose_true(capsys) -> None:
    log = make_logger("wiener", verbose=True)

    log("start")
    log("fallback marker", level="unknown")
    log.found("recovered d")
    log.fail("constraint not met")
    log.warn("beta may be too small")

    captured = capsys.readouterr().out.splitlines()
    assert captured[0] == "[wiener] . start"
    assert captured[1] == "[wiener] . fallback marker"
    assert captured[2] == "[wiener] OK recovered d"
    assert captured[3] == "[wiener] FAIL constraint not met"
    assert captured[4] == "[wiener] WARN beta may be too small"
