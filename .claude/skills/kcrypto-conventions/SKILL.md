---
name: kcrypto-conventions
description: Use when creating or modifying files in kcrypto attacks or analyze modules, or when changing architecture-sensitive contracts, logging, optional dependency behavior, or agent-facing project conventions.
---

# kcrypto Conventions

## Overview

This skill is the architecture guardrail for kcrypto and is treated as hard rules.

Priority order:
1. Direct user instruction
2. System/developer constraints
3. This skill

Core principle: preserve architecture contracts first, then optimize implementation details.

## When to Use

Use this skill when:
- Creating new files in `kcrypto/attacks/` or `kcrypto/analyze/`
- Modifying attack or analysis interfaces
- Touching `Result`, `Finding`, logger, or optional dependency bridge behavior
- Changing public API behavior, docstrings, or AGENTS guidance

Do not skip for "small" changes in attacks or analyze.

## Hard Rules

1. Tier classification is mandatory for attacks.
2. Dynamic attacks return `Result`; static analysis returns `Finding` or `list[Finding]`.
3. Public attack failure flow must return `Result(success=False, error=...)`; do not leak normal failures as exceptions.
4. Keep logger pattern consistent with `make_logger` semantics (`step`, `found`, `fail`, `warn`).
5. New public API symbols require Google-style docstrings.
6. Optional dependencies are lazy and graceful: core imports must still work without Sage/z3/pwn.
7. Do not call direct `sage.factor(...)` in attack flows; use factoring dispatcher.
8. If interface/convention changes, update AGENTS guidance in scope.

## Tier Execution Contract

### Decision Gate (must follow in order)

1. Does any normal execution path interact with an external oracle/network/server callback?
- Yes: Tier 3 (even if callback is optional/configurable)
- No: go to step 2

2. Does it need inspectable/retryable intermediate state across steps?
- Yes: Tier 2
- No: Tier 1

Never choose tier by coding convenience.
If a solution can succeed only when oracle interaction is enabled, classify it as Tier 3.

### Tier 1 Template (pure function)

```python
from __future__ import annotations

import time
from typing import Any

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "domain/attack_name"  # canonical catalog key — one per module


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


def attack_name(..., *, verbose: bool = False) -> Result:
    """<One-sentence description.>

    Args:
        ...: ...
        verbose: If True, print progress. Default False.

    Returns:
        Result with data["key"] on success.
        Result with success=False if <failure condition>.

    Raises:
        Nothing. All failures encoded as Result(success=False, error=...).
    """
    log = make_logger(_ATTACK, verbose)
    start = time.time()

    try:
        log("Starting attack", "step")
        # TODO: implement — Human fills
        raise NotImplementedError
    except SomeExpectedError as e:
        msg = f"Attack failed: {e}"
        log(msg, "fail")
        return _fail(msg, start)
    except Exception as e:
        msg = f"Unexpected error: {type(e).__name__}: {e}"
        log(msg, "fail")
        return _fail(msg, start)
```

### Tier 2 Template (stateful object)

```python
from __future__ import annotations

import time
from dataclasses import dataclass, field

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "domain/attack_name"


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


@dataclass
class AttackState:
    step_output: object | None = None
    meta: dict = field(default_factory=dict)


class AttackName:
    def __init__(self, ..., *, verbose: bool = False):
        self._log = make_logger(_ATTACK, verbose)
        self._start = time.time()
        self.state = AttackState(meta={...})

    def build(self) -> "AttackName":
        # TODO: implement — Human fills
        raise NotImplementedError
        return self

    def extract(self) -> Result:
        ok = ...
        return Result(
            success=ok,
            attack=_ATTACK,
            data={...},
            artifacts={"state": self.state},
            error=None if ok else "reason",
            elapsed=(time.time() - self._start) * 1000,
        )
```

### Tier 3 Template (oracle/external interaction)

```python
from __future__ import annotations

import time
from collections.abc import Callable

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "domain/attack_name"


def _fail(error: str, start: float) -> Result:
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


class AttackNameOracle:
    def __init__(self, oracle: Callable[[bytes], bool], ..., *, verbose: bool = False):
        self._oracle = oracle
        self._log = make_logger(_ATTACK, verbose)
        self._start = time.time()

    def run(self, ...) -> Result:
        trace = []
        # TODO: oracle interaction loop — Human fills
        raise NotImplementedError
        ok = ...
        return Result(
            success=ok,
            attack=_ATTACK,
            data={...},
            artifacts={"trace": trace},
            error=None if ok else "reason",
            elapsed=(time.time() - self._start) * 1000,
        )
```

## Docstring Convention

Public functions/classes in `kcrypto/attacks/` and `kcrypto/analyze/` require Google-style docstrings.

**4 required sections** (in order):

1. **Summary line** — one sentence, what the attack does (not how)
2. **Args** — every parameter; `verbose` always last; describe `**kwargs` common keys
3. **Returns** — `data` keys on success AND failure condition phrasing
4. **Raises** — always `Nothing. All failures encoded as Result(success=False, error=...).`

**Example section**: omit in scaffolds; add only after implementation is complete and tested.

**Inline comments**:
- Algorithm step labels: `# Step 1: build continued fraction convergents`
- Non-obvious thresholds: `# Wiener bound: attack works when d < n^0.25 / 3`
- Human TODO blocks: `# TODO: <description> — Human implements`
- Do NOT comment self-evident code

**Module docstring**: one line, mandatory.
```python
"""<Attack name> attack implementation."""
```

## Testing Minimums

- Tier 1: known-answer + contract test (`Result` returned on fail path)
- Tier 2: contract test + state inspection/retry test
- Tier 3: contract test + mocked oracle integration test
- When practical: property test for vulnerable parameter families

Fixtures must be pre-generated and committed.

## Red Flags - Stop and Fix

- Returning `Result` from analyze logic
- Throwing `ValueError` in normal attack failure path
- Direct use of `sage.factor(...)` in attack code
- Missing public docstring for new API symbol
- Behavior contract change without AGENTS update

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "This is tiny, rules are overkill." | Small contract drift compounds across sessions. |
| "I used `sage.factor` only for quick success." | This bypasses timeout/fallback architecture and risks hangs. |
| "I will update docs later." | Delayed sync creates agent drift and wrong future edits. |
| "Result vs Finding are similar enough." | Mixing them breaks analyze/attack boundaries. |

## Pre-Completion Checklist

- Tier selected via decision gate
- Module output contract correct (`Result` vs `Finding`)
- Failure path encoded as data, not crash
- Logger semantics preserved
- Public docstrings present
- Optional dependency behavior remains lazy and clear
- AGENTS guidance updated when behavior contract changed
- Relevant tests added or updated
