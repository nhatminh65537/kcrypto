# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`kcrypto` is a Python library aggregating cryptography attacks for CTF and security research. It is in **skeleton-first** phase — infrastructure is implemented, attack logic is mostly scaffold.

Key constraint: **core crypto algorithm logic is Human-owned**. Claude scaffolds structure, contracts, tests, and glue. Humans fill algorithm `TODO` blocks. Do not implement crypto math without explicit Human approval.

## Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests
python -m pytest tests/

# Run a single test file
python -m pytest tests/attacks/lattice/test_lll.py -v

# Run a single test by name
python -m pytest tests/attacks/lattice/test_lll.py::test_name -v

# Type check
mypy kcrypto/
```

## Architecture

Four layers, strict one-way dependency flow (upper → lower):

1. **User-Facing Surface** — public `kcrypto/` exports, docs, `AGENTS.md`
2. **Analysis** — `kcrypto/analyze/`: static analysis returning `Finding` objects
3. **Attacks** — `kcrypto/attacks/<domain>/`: domain-grouped attack implementations
4. **Core & Bridges** — `kcrypto/core/`: primitives; `kcrypto/bridges/`: optional dep adapters

### 3-Tier Attack Model

| Tier | When | Pattern |
|------|------|---------|
| T1 | Single-pass, no intermediate state needed | Pure function returning `Result` |
| T2 | Multi-stage, inspectable steps | Stateful class; `__init__` locks params, step methods return `self`, terminal method returns `Result` |
| T3 | External oracle/network required | Same as T2 + injected oracle callback |

### Core Contracts

**`Result`** (from `kcrypto/core/contracts.py`) — all attack outputs:
- Required: `success`, `attack`, `data`, `artifacts`, `error`, `elapsed`
- `success=True` → `error=None`; `success=False` → `error` explains why
- `data` = primary outputs; `artifacts` = intermediate values for inspection

**`Finding`** — all analyze outputs:
- Fields: `name`, `confidence` (0.0–1.0), `reason`, `suggested`, `params`

**Logger** — use `make_logger("attack_name", verbose)` from `kcrypto/core/logger.py`. Markers: step `.`, found `OK`, fail `FAIL`, warn `WARN`.

### Attack Naming

Catalog key format: `domain/action` (e.g., `rsa/wiener_attack`, `factoring/smart_attack`). Set in `Result.attack` and `Finding.suggested`. See `AGENTS.md §5.6` for full alias list.

## Hard Rules

1. **Factoring rule**: Never call `sage.factor()` directly in attack modules. Route through `from kcrypto.attacks.factoring import factor`.
2. **Optional dependencies**: Must be lazy-loaded via `kcrypto/bridges/`. `import kcrypto` must succeed even without Sage/z3/pwntools.
3. **Return `Result`, never raise**: All attack failure paths return `Result(success=False, error=...)`.
4. **Don't claim done without running pytest**: At minimum, run scoped `pytest` before completing any task.
5. **Don't change public signatures** without synchronized updates to tests, docs, and `AGENTS.md`.

## Key Reference Files

- `AGENTS.md` — full conventions, workflow, and responsibilities (read before any work)
- `docs/dev/architecture.md` — architecture details and code examples per tier
- `docs/dev/module-progress-cheatsheet.md` — current implementation status per module
- `kcrypto/core/contracts.py` — `Result` and `Finding` implementations
- `kcrypto/core/logger.py` — `make_logger` implementation

## Implementation Status

Most attack modules are **SCAFFOLD** (stubs only). Implemented:
- `kcrypto/core/contracts.py`, `kcrypto/core/logger.py`
- `kcrypto/attacks/lattice/` — `lll_reduce()`, `bkz_reduce()` (Tier 1, fully tested)
- `kcrypto/bridges/sage.py` — SageMath adapter

Tests live in `tests/` mirroring `kcrypto/` structure. Fixtures must be pre-generated and committed — no dynamic fixture generation from optional deps in test runs.
