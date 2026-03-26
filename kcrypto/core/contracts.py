"""Contracts for attack results and analyzer findings.

This module provides structure-only scaffolds for the canonical output
contracts used across kcrypto.
"""

from __future__ import annotations

from html import escape
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Result:
    """Dynamic attack output contract.

    Fields:
        success: True if the attack succeeded.
        attack: Attack name, such as "wiener" or "coppersmith".
        data: Primary attack outputs.
        artifacts: Intermediate state for inspection/replay.
        error: Failure reason when success is False.
        elapsed: Execution time in milliseconds.
    """

    success: bool
    attack: str
    data: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    elapsed: float = 0.0

    def __getitem__(self, key: str) -> Any:
        """Return an item from data by key.

        Args:
            key: Data key.

        Returns:
            Data value for the given key.
        """
        return self.data[key]

    def __getattr__(self, key: str) -> Any:
        """Provide attribute-style access for data keys.

        Args:
            key: Data key.

        Returns:
            Data value for the given key.
        """
        data = object.__getattribute__(self, "data")
        if key in data:
            return data[key]
        raise AttributeError(key)

    def __repr__(self) -> str:
        """Return concise notebook-friendly representation.

        Returns:
            Text representation for terminal/IPython usage.
        """
        status = "OK" if self.success else "FAIL"
        lines = [f"Result({status} {self.attack}, {self.elapsed:.0f}ms)"]
        if self.success:
            for key, value in self.data.items():
                lines.append(f"  {key} = {repr(value)[:60]}")
        else:
            lines.append(f"  error = {self.error}")
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        """Return HTML representation for rich notebook display.

        Returns:
            HTML representation of this result.
        """
        status = "success" if self.success else "failure"
        rows = [
            f"<tr><th>attack</th><td>{escape(self.attack)}</td></tr>",
            f"<tr><th>status</th><td>{status}</td></tr>",
            f"<tr><th>elapsed_ms</th><td>{self.elapsed:.3f}</td></tr>",
        ]

        if self.success:
            for key, value in self.data.items():
                rows.append(
                    f"<tr><th>{escape(str(key))}</th><td>{escape(repr(value))}</td></tr>"
                )
        else:
            rows.append(f"<tr><th>error</th><td>{escape(str(self.error))}</td></tr>")

        return "<table>" + "".join(rows) + "</table>"


@dataclass(slots=True)
class Finding:
    """Static analysis output contract.

    Fields:
        name: Stable finding key (for example, "wiener_candidate").
        confidence: Probability-like score in [0.0, 1.0].
        reason: Human-readable explanation.
        suggested: Recommended attack name, if any.
        params: Computed metadata used during analysis.
    """

    name: str
    confidence: float
    reason: str
    suggested: str | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        """Return concise notebook-friendly representation.

        Returns:
            Text representation for terminal/IPython usage.
        """
        lines = [f"Finding({self.name}, confidence={self.confidence:.2f})"]
        lines.append(f"  reason = {self.reason}")
        lines.append(f"  suggested = {self.suggested}")
        if self.params:
            for key, value in self.params.items():
                lines.append(f"  param[{key}] = {value}")
        return "\n".join(lines)

    def _repr_html_(self) -> str:
        """Return HTML representation for rich notebook display.

        Returns:
            HTML representation of this finding.
        """
        rows = [
            f"<tr><th>name</th><td>{escape(self.name)}</td></tr>",
            f"<tr><th>confidence</th><td>{self.confidence:.3f}</td></tr>",
            f"<tr><th>reason</th><td>{escape(self.reason)}</td></tr>",
            f"<tr><th>suggested</th><td>{escape(str(self.suggested))}</td></tr>",
        ]
        for key, value in self.params.items():
            rows.append(
                f"<tr><th>param[{escape(str(key))}]</th><td>{escape(repr(value))}</td></tr>"
            )
        return "<table>" + "".join(rows) + "</table>"
