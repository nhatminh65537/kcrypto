# kcrypto Architecture and Development Rules

This document defines the architecture, invariants, and engineering rules for kcrypto.
Use it as a development contract when adding or modifying modules.

## 1. System Goals

- Provide a Python-first cryptography attack library for CTF and security research workflows.
- Keep modules inspectable (glass-box), not opaque black-box executors.
- Support iterative extension without breaking public compatibility.
- Work naturally in IPython/Jupyter and script-based pipelines.

## 2. Design Principles

- Glass-box by default: intermediate state must be visible through `artifacts` or object `state`.
- API-first: modules are designed for import and composition, not CLI-centric execution.
- Analyze first, attack second: static heuristics and dynamic exploitation are separate phases.
- Fail as data, not crashes: attack entrypoints return `Result` instead of propagating runtime failures.
- Extension-friendly architecture: new attacks should be addable with minimal cross-module edits.

## 3. Four-Layer Architecture

### Layer 1: User-Facing Surface

- Public package API (`kcrypto/...` exports).
- User/developer docs.
- Agent-facing instructions in AGENTS.md.

Primary concern: usability, discoverability, and stable contracts.

### Layer 2: Analysis and Intelligence

- Static analyzers in `kcrypto/analyze/`.
- Structured findings that suggest likely attacks.

Primary concern: fast vulnerability triage without executing expensive attack logic.

### Layer 3: Attack Modules

- Domain-specific attacks in `kcrypto/attacks/`.
- Implemented using a tier model (Tier 1/2/3).

Primary concern: deterministic behavior, inspectable state, and strong result contracts.

### Layer 4: Core and Bridges

- `kcrypto/core/`: low-level reusable primitives and utilities.
- `kcrypto/bridges/`: optional dependency adapters (SageMath, z3, pwntools).

Primary concern: clean dependency boundaries and graceful optional integrations.

## 4. Dependency Rules and Optional Dependency Policy

- Dependency flow is one-way from upper layers to lower layers.
- `core` must not depend on heavy or attack-specific toolchains.
- Optional integrations must be lazy-loaded through bridge modules.
- `import kcrypto` must succeed even when optional dependencies are missing.
- Missing optional dependencies must raise clear, actionable errors only at call-time.

Example pattern:

```python
# kcrypto/bridges/sage.py
class _MissingSage:
	def __getattr__(self, name: str):
		raise ImportError(
			"This feature requires SageMath. "
			"See installation docs for optional dependencies."
		)


try:
	from sage.all import ZZ, QQ, matrix, vector  # type: ignore
	SAGE_AVAILABLE = True
except ImportError:
	ZZ = QQ = matrix = vector = _MissingSage()
	SAGE_AVAILABLE = False
```

## 5. Attack Module Tier Model

### Tier 1: Pure Function

Use Tier 1 when:

- The algorithm is mostly single-pass.
- Stateful retries are unnecessary.
- Inputs and outputs are straightforward.

Rules:

- Return `Result`.
- Keep inputs explicit.
- Include intermediate data in `artifacts` when useful for debugging.

Example:

```python
from kcrypto._result import Result


def wiener(e: int, N: int, c: int | None = None, verbose: bool = False) -> Result:
	convergents = _continued_fraction(e, N)
	for k, d in convergents:
		if _candidate_is_valid(e=e, N=N, k=k, d=d):
			m = pow(c, d, N) if c is not None else None
			return Result(
				success=True,
				attack="wiener",
				data={"d": d, "m": m},
				artifacts={"convergents": convergents},
				error=None,
				elapsed=0.0,
			)

	return Result(
		success=False,
		attack="wiener",
		data={},
		artifacts={"convergents": convergents},
		error="Wiener preconditions not satisfied.",
		elapsed=0.0,
	)
```

### Tier 2: Stateful Object

Use Tier 2 when:

- The attack has multiple stages.
- Developers need to inspect and retry intermediate steps.
- Strategy components (reducers, extractors) should be injectable.

Rules:

- Constructor stores immutable problem parameters.
- Step methods mutate internal state and return `self` for chaining.
- Terminal method returns `Result`.

Example:

```python
from dataclasses import dataclass, field
from typing import Any

from kcrypto._result import Result


@dataclass
class CoppersmithState:
	matrix: Any = None
	reduced_basis: Any = None
	roots: list[int] = field(default_factory=list)


class Coppersmith:
	def __init__(self, f: Any, N: int, beta: float = 0.5):
		self.f = f
		self.N = N
		self.beta = beta
		self.state = CoppersmithState()

	def build(self) -> "Coppersmith":
		self.state.matrix = _build_lattice(self.f, self.N, self.beta)
		return self

	def reduce(self) -> "Coppersmith":
		self.state.reduced_basis = _lll(self.state.matrix)
		return self

	def extract(self) -> Result:
		roots = _extract_roots(self.state.reduced_basis)
		self.state.roots = roots
		ok = len(roots) > 0
		return Result(
			success=ok,
			attack="coppersmith",
			data={"roots": roots},
			artifacts={"state": self.state},
			error=None if ok else "No valid small roots found.",
			elapsed=0.0,
		)
```

### Tier 3: External Oracle Interaction

Use Tier 3 when:

- External systems are queried (network services, challenge servers, oracles).
- Data collection and exploitation logic should remain separable.

Rules:

- Keep transport/oracle code isolated from core attack math.
- Define callback or protocol interfaces explicitly.
- Preserve reproducibility by storing interaction traces in `artifacts`.

## 6. Stable Contracts

All attack modules must follow common data contracts.

### Result Contract (Dynamic Attack Output)

Required fields:

- `success: bool`
- `attack: str`
- `data: dict`
- `artifacts: dict`
- `error: str | None`
- `elapsed: float`

Behavioral requirements:

- On success: `success=True`, `error=None`.
- On failure: `success=False`, `error` must explain why.
- `data` contains primary outputs.
- `artifacts` contains intermediate values useful for inspection/replay.

### Finding Contract (Static Analysis Output)

Expected fields:

- `name`: unique finding key.
- `confidence`: probability-like score in `[0.0, 1.0]`.
- `reason`: human-readable explanation.
- `suggested`: recommended attack name or `None`.
- `params`: computed analysis metadata.

### Logger Contract

All modules should use a consistent log style:

- Prefix: `[attack_name]`
- Markers: step (`.`), found (`OK`), fail (`FAIL`), warn (`WARN`)
- Respect `verbose=False` by staying silent.

Example:

```python
def make_logger(name: str, verbose: bool):
	markers = {"step": ".", "found": "OK", "fail": "FAIL", "warn": "WARN"}

	def log(message: str, level: str = "step") -> None:
		if verbose:
			print(f"[{name}] {markers.get(level, '.')} {message}")

	return log
```

## 7. Factoring Policy (Hard Rule)

Do not call `sage.factor(N)` directly inside attack modules.

Always route factoring through the dispatcher:

```python
from kcrypto.attacks.factoring import factor
```

Required dispatcher behavior:

- Light-to-heavy strategy progression.
- Per-method timeout controls.
- Graceful fallback with partial factors when full factorization is not feasible.

Suggested method order:

1. Perfect power detection.
2. Trial division.
3. Fermat (bounded iterations).
4. Pollard rho (timeout bound).
5. ECM via SageMath (if available, timeout bound).
6. yafu wrapper (if binary exists, subprocess timeout).
7. msieve wrapper (backup, subprocess timeout).

Partial result example:

```python
return Result(
	success=False,
	attack="factor",
	data={"partial": [p1, p2], "remaining": rem},
	artifacts={"method_trace": tried_methods},
	error="Incomplete factorization within current time and tool limits.",
	elapsed=elapsed_ms,
)
```

## 8. Testing Rules

Every non-trivial attack should include:

1. Known-answer tests using committed fixtures.
2. Contract tests validating `Result` behavior in success and failure paths.
3. Property-based tests (when practical) for broader confidence.
4. Integration tests for `analyze -> attack` workflows.

Hard rules:

- Fixtures must be pre-generated and committed.
- Tests must be deterministic by default.
- Failure paths must return `Result`; do not leak exceptions to the test runner.

Example contract test:

```python
from kcrypto._result import Result
from kcrypto.attacks.rsa import wiener


def test_wiener_always_returns_result(wiener_fixture):
	r = wiener(e=65537, N=wiener_fixture["N"])
	assert isinstance(r, Result)
	assert r.success is False
	assert r.error is not None
```

## 9. Documentation Rules

- Public classes and functions must have Google-style docstrings.
- Docstrings are the canonical source for API docs generation.
- Include preconditions, limitations, return schema, and a minimal usage example.
- Add references for algorithmic sources when applicable.

Docstring skeleton:

```python
def attack_name(param1: int, param2: int, verbose: bool = False) -> Result:
	"""One-line summary.

	Extended description of assumptions and limitations.

	Args:
		param1: Description.
		param2: Description.
		verbose: Enables progress logs.

	Returns:
		Result where data contains: key_a, key_b.

	Example:
		>>> r = attack_name(1, 2, verbose=True)
		>>> if r.success:
		...     print(r.data["key_a"])
	"""
```

## 10. Directory Boundaries

- `kcrypto/core/`: reusable low-level primitives with minimal dependencies.
- `kcrypto/analyze/`: static risk indicators and attack recommendations.
- `kcrypto/attacks/`: executable attack implementations.
- `kcrypto/attacks/factoring/`: factoring orchestration and tool wrappers.
- `kcrypto/bridges/`: optional dependency adapters and capability flags.

Do not move logic across boundaries unless architecture-level rationale is documented.

## 11. New Attack Checklist

1. Choose the correct tier (Tier 1/2/3).
2. Implement complete `Result` handling for all paths.
3. Expose useful intermediate values through `artifacts` or object `state`.
4. Add clear Google-style docstrings.
5. Add known-answer and contract tests; add property/integration tests when feasible.
6. Route optional dependencies through `bridges/`.
7. Preserve module boundaries (`core`, `analyze`, `attacks`, `bridges`).

## 12. Environment Baseline

Core runtime:

- Python >= 3.11
- gmpy2 >= 2.1
- pycryptodome >= 3.18

Optional tooling (environment-provided):

- SageMath >= 10.0
- z3-solver >= 4.12
- pwntools >= 4.11
- yafu binary
- msieve binary

## 13. Minimal End-to-End Usage Example

```python
from kcrypto.analyze.rsa import rsa_analyze
from kcrypto.attacks.rsa import wiener


findings = rsa_analyze(e=e, N=N)
best = max(findings, key=lambda f: f.confidence, default=None)

if best and best.suggested == "wiener":
	result = wiener(e=e, N=N, c=c, verbose=True)
	if result.success:
		print("Recovered d:", result.data["d"])
	else:
		print("Attack failed:", result.error)
```
