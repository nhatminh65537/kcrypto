# AGENTS.md - kcrypto

> Read this file before doing any work. This is the source of truth for conventions, workflow, and Agent/Human responsibilities in this project.

---

## 1. Project Overview

`kcrypto` is a Python library that aggregates cryptography attacks for CTF and security research.

- Language: Python 3.11+
- Test runner: pytest
- Doc style: Google-style docstrings
- Optional dependencies: Sage (`kcrypto[sage]`), z3 (`kcrypto[z3]`), pwntools (`kcrypto[pwn]`)
- Package root: `kcrypto/`
- Current status: skeleton-first, many modules are still in scaffold phase

---

## 2. Responsibilities - IMPORTANT

| Task | Owner | Notes |
|------|-------|-------|
| Scaffold files, skeleton classes/functions | Agent | Correct naming and correct tier |
| Write and standardize docstrings | Agent | Google style, clear constraints |
| Wrap outputs in `Result` / `Finding` | Agent | Follow strict contracts |
| Hook logger checkpoints | Agent | Do not miss failure paths |
| Write test skeletons + fixture plumbing | Agent | TODO allowed if expected Sage outputs are unavailable |
| Run pytest and report results | Agent | Mandatory gate before completion claims |
| Update AGENTS when public contracts change | Agent | Top-level or per-module guidance |
| Core crypto algorithm logic | Human | Agent MUST NOT fill core math by itself |
| Critical private crypto-math helpers | Human | Agent leaves TODO or `raise NotImplementedError("Human implements")` |
| Review algorithm correctness | Human | |
| Merge PR / publish release | Human | |

Principle: Agent provides high-quality structure (API, contracts, tests, docs). Human fills core cryptographic math.

---

## 3. 3-Tier Attack System

### Tier 1 - Pure Function

```python
from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger

_ATTACK = "rsa/wiener_attack"  # canonical catalog key — one per module


def _fail(error: str, start: float) -> Result:
    """Shared failure helper — avoids repeating Result(success=False, ...) boilerplate."""
    import time
    return Result(
        success=False,
        attack=_ATTACK,
        error=error,
        elapsed=(time.time() - start) * 1000,
    )


def wiener_attack(e: int, n: int, *, verbose: bool = False) -> Result:
    """<One-sentence description of what the attack does.>

    Args:
        e: Public exponent.
        n: RSA modulus.
        verbose: If True, print progress. Default False.

    Returns:
        Result with data["d"] on success.
        Result with success=False if continued fraction expansion yields no solution.

    Raises:
        Nothing. All failures encoded as Result(success=False, error=...).
    """
    import time
    log = make_logger(_ATTACK, verbose)
    start = time.time()

    log("Starting Wiener attack", "step")
    # TODO: implement continued fraction convergents — Human implements
    raise NotImplementedError
```

Rules:
- `_ATTACK` module-level constant — avoids string duplication across `Result` returns
- `_fail()` module-level helper — avoids repeating `Result(success=False, ...)` in every except block
- `import time` inside function for modules without Sage dependency; at top-level otherwise
- No multi-step inspectable state is required
- Direct input → output flow

### Tier 2 - Stateful Object

```python
@dataclass
class MyAttackState:
    step_output: object | None = None


class MyAttack:
    def __init__(self, *, verbose: bool = False):
        self._log = make_logger("my_attack", verbose)
        self.state = MyAttackState()

    def step(self) -> "MyAttack":
        # TODO: implement
        raise NotImplementedError("Human implements")

    def finish(self) -> Result:
        return Result(...)
```

- Parameters are locked in `__init__`
- State accumulates across steps
- Step methods should return `self` for chaining when appropriate

### Tier 3 - Oracle-Based Object

- Same as Tier 2, plus an external oracle/callback injected in `__init__`
- Prefer explicit and typed oracle interfaces
- Do not merge fundamentally different tiers into one class

---

## 4. Core Contracts

### 4.1 Attack Outputs

- Dynamic attack APIs must return `Result`
- Analyze APIs must return `Finding` or `list[Finding]`
- Normal failure paths must be encoded as `Result(success=False, error=...)`, not thrown as expected exceptions

### 4.2 Logger

- Use `make_logger("attack_name", verbose)` consistently
- Checkpoints should include: progress, found, fail

### 4.3 Interface Stability

- Do not change public signatures without explicit request
- If contract changes are necessary: update tests + docs + AGENTS in the same task

---

## 5. Mandatory Rules

### 5.1 Factoring Rule

- NEVER call `sage.factor(...)` directly in attack flows outside factoring modules
- When factoring is needed in other attacks, route through the package factoring dispatcher/API

### 5.2 Optional Dependencies

- Core imports must work even when Sage/z3/pwn are not installed
- Lazy-load optional dependencies with clear install guidance in failure messages

### 5.3 Docstrings

Public functions/classes in `kcrypto/attacks/` and `kcrypto/analyze/` must use Google-style docstrings.

**4 required sections** (in this order):

1. **Summary line** — one sentence, what the attack does (not how)
2. **Args** — every parameter; for `**kwargs` describe common keys
3. **Returns** — `data` keys on success AND failure condition phrasing
4. **Raises** — always `Nothing. All failures encoded as Result(success=False, error=...)`.

**Example section**: omit in scaffolds; add only after implementation is complete and tested.

**Inline comments**: only when logic is not self-evident. Required for:
- Algorithm step labels: `# Step 1: build continued fraction convergents`
- Non-obvious thresholds: `# Wiener bound: attack works when d < n^0.25 / 3`
- Human TODO blocks: `# TODO: <description> — Human implements`

**Module docstring**: one line, mandatory.

```python
"""<Attack name> attack implementation."""
```

### 5.4 Tests

- Every attack must have at least: success case + failure case + edge case
- If fixtures require Sage-generated values, keep scripts/repro steps committed

### 5.5 AGENTS Synchronization

- When adding/changing public symbols or behavior contracts, update AGENTS in the same task

### 5.6 Attack Naming Standardization (Human-Readable)

Use naming that is clear, consistent, and recognizable to humans.

#### 5.6.1 Canonical formats

Use two canonical IDs with one style:

- Catalog key (for dispatch/docs): `domain/action`
  - Regex: `^[a-z][a-z0-9_]*(/[a-z][a-z0-9_]*)$`
- Leaf action (for internals where needed): `action` in snake_case
  - Regex: `^[a-z][a-z0-9_]*$`

Primary contract fields:

- `Result.attack`: SHOULD use catalog key (`domain/action`) for clarity and uniqueness
- `Finding.suggested`: SHOULD use the same catalog key
- Tests, fixtures, and docs should use the same canonical key

#### 5.6.2 Naming pattern (noun-style, consistency-first)

Use noun-style canonical names whenever possible.
If an attack has a well-known method name, keep that method token in the canonical key.

Recommended patterns:

- Method-first (noun phrase): `<domain>/<method>_<noun_context>`
- Generic noun style when method is unknown/secondary: `<domain>/<noun_context>`
- Keep stable, already-readable names unchanged for compatibility (for example: `smart_attack`, `fermat_factorization`)

Examples:

- `rsa/fermat_factorization`
- `rsa/wiener_attack`
- `rsa/boneh_durfee_attack`
- `rsa/known_d_factorization`
- `rsa/known_phi_factorization`
- `factoring/smart_attack`

Rationale:

- Readers instantly recognize common attacks (`fermat`, `wiener`, `coppersmith`)
- Keys remain consistent and machine-normalizable
- Catalog names stay informative without losing standard terminology
- Existing stable names are preserved; only inconsistent names should be normalized

#### 5.6.3 Normalization pipeline

1. `strip()` and lowercase
2. Replace `-`, whitespace, `.`, and `:` with `_`
3. Collapse repeated `_`
4. Normalize separators to exactly one `/` between domain and action when possible
5. Map known aliases/misspellings to canonical keys
6. Validate with canonical regex
7. If invalid, fail clearly with `Result(success=False, error=...)`

#### 5.6.4 Alias seed (extend over time)

- `rsa/know_d_factor` -> `rsa/known_d_factorization`
- `rsa/known_phi` -> `rsa/known_phi_factorization`
- `rsa/fermat` -> `rsa/fermat_factorization`
- `wienner` -> `rsa/wiener_attack`
- `franklinreiter` -> `rsa/franklin_reiter_attack`
- `factoring/smart` -> `factoring/smart_attack`

#### 5.6.5 New attack checklist

- Choose canonical `domain/action` key before merging skeleton
- Add aliases for common input mistakes
- Sync cheatsheet and contract tests for dispatcher naming behavior

### 5.7 Cheatsheet Requirement

- Maintain a quick project status cheatsheet at `docs/dev/module-progress-cheatsheet.md`
- Update it whenever module implementation status or naming conventions change
- Keep it short, scan-friendly, and aligned with current tests

---

## 6. Skill Workflow in This Repo

Skills are located in `.github/skills/`.

| Skill | When to use |
|-------|-------------|
| `kcrypto-conventions` | Changes in `kcrypto/attacks/`, `kcrypto/analyze/`, or architecture-sensitive contracts |
| `test-driven-development` | Before implementing a feature/bugfix |
| `systematic-debugging` | When tests fail or behavior is unexpected |
| `writing-plans` | Multi-step tasks requiring explicit execution plans |
| `verification-before-completion` | Before claiming work is done |
| `requesting-code-review` | Before merge for substantial changes |
| `finishing-a-development-branch` | After verification passes and integration is prepared |

### Attack implementation loop (summary)

```text
Agent: scaffold + test skeleton/fixture plumbing
    ->
Human: fill core crypto algorithm TODO blocks
    ->
Agent: complete glue (Result/Finding wrap, logger hooks, timing)
    ->
Agent: run pytest + verify contracts
    -> [fail] isolate: glue issue -> Agent fix | algorithm issue -> Human fix
    -> [pass]
Move to the next module/attack
```

---

## 7. OpenMemory MCP

Project uses OpenMemory for cross-session context. Agent should:

- Before session: load relevant memory (phase/batch/decisions)
- After milestones: store short metadata only (status, tier, decision), no large data dumps

Suggested format:

```text
kcrypto | kcrypto/attacks/rsa/wiener.py | status: done | tier: T1 | verify: pytest-pass
kcrypto | phase: scaffold | module: rsa | next: hastad skeleton
kcrypto | decision: keep factoring dispatcher as single entrypoint
```

---

## 8. Directory Layout (Current)

```text
AGENTS.md
CLAUDE.md
pyproject.toml
README.md
docs/
  dev/
    architecture.md
    module-progress-cheatsheet.md
  user/
    <domain>/          # user-facing attack tutorials
kcrypto/
  __init__.py
  core/
    contracts.py       # Result, Finding
    logger.py          # make_logger
  bridges/
    sage.py            # SageMath lazy adapter
    z3.py              # z3-solver lazy adapter
    pwn.py             # pwntools lazy adapter
  analyze/
  attacks/
    <domain>/
      __init__.py      # re-exports public functions
      <attack>.py      # one attack per file
tests/
  attacks/
    <domain>/
      test_<attack>.py
```

Notes:

- Attack modules live in `kcrypto/attacks/<domain>/`
- Analyze modules live in `kcrypto/analyze/`
- Optional dependency bridges live in `kcrypto/bridges/`
- Each domain has an `__init__.py` that explicitly re-exports public symbols

---

## 9. Agent Must NOT Do

- Fill core crypto algorithm TODO blocks without Human approval
- Change public contracts implicitly (signatures/output schema/data keys) without synchronized docs/tests updates
- Bypass factoring architecture by calling direct APIs in non-factoring attack flow
- Claim completion without relevant verification (at least scoped pytest)
- Commit directly to `main` unless explicitly requested

---

## 10. Definition of Done for an Attack/Module

- API skeleton or implementation matches the correct tier
- `Result` / `Finding` contract is correct
- Logger checkpoints are meaningful
- Related tests are added and run
- Docs and AGENTS are synchronized with current behavior
