# kcrypto Module Progress Cheatsheet

Quick progress snapshot for users, developers, and agents.

Last updated: 2026-03-27

## 1. Status Legend

- SCAFFOLD: file/module exists with docstring or placeholder only.
- CONTRACT-READY: core contracts/utilities implemented and tested.
- IMPLEMENTED: functional algorithm/logic implemented (none in attack/analyze at this snapshot).

## 2. Quick Inventory Summary

| Area | Total files | Implemented | Scaffold |
|---|---:|---:|---:|
| `kcrypto/attacks/` (python files) | 24 | 0 | 24 |
| `kcrypto/analyze/` (python files) | 3 | 0 | 3 |
| `kcrypto/core/` (python files) | 6 | 2 (`contracts.py`, `logger.py`) | 4 |

## 3. Attack Modules (Current Snapshot)

### 3.1 Domain Packages

| Module | Status | Notes |
|---|---|---|
| `kcrypto.attacks.dlog` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.ecc` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.factoring` | SCAFFOLD | package + wrappers/dispatcher skeletons |
| `kcrypto.attacks.hash` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.isogeny` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.lattice` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.rsa` | SCAFFOLD | package + attack file skeletons |
| `kcrypto.attacks.secret_sharing` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.signatures` | SCAFFOLD | package `__init__` only |
| `kcrypto.attacks.symmetric` | SCAFFOLD | package `__init__` only |

### 3.2 RSA Attack Files

| File | Status |
|---|---|
| `kcrypto/attacks/rsa/wiener.py` | SCAFFOLD |
| `kcrypto/attacks/rsa/hastad.py` | SCAFFOLD |
| `kcrypto/attacks/rsa/fermat.py` | SCAFFOLD |
| `kcrypto/attacks/rsa/coppersmith.py` | SCAFFOLD |
| `kcrypto/attacks/rsa/boneh_durfee.py` | SCAFFOLD |
| `kcrypto/attacks/rsa/franklin_reiter.py` | SCAFFOLD |
| `kcrypto/attacks/rsa/bleichenbacher.py` | SCAFFOLD |

### 3.3 Factoring Attack Files

| File | Status |
|---|---|
| `kcrypto/attacks/factoring/pollard_rho.py` | SCAFFOLD |
| `kcrypto/attacks/factoring/ecm.py` | SCAFFOLD |
| `kcrypto/attacks/factoring/yafu.py` | SCAFFOLD |
| `kcrypto/attacks/factoring/msieve.py` | SCAFFOLD |
| `kcrypto/attacks/factoring/smart.py` | SCAFFOLD |

## 4. Analyze Modules (Current Snapshot)

| File | Status | Notes |
|---|---|---|
| `kcrypto/analyze/rsa.py` | SCAFFOLD | module placeholder |
| `kcrypto/analyze/ecc.py` | SCAFFOLD | module placeholder |
| `kcrypto/analyze/__init__.py` | SCAFFOLD | package scaffold |

## 5. Core Modules (Current Snapshot)

| File | Status | Notes |
|---|---|---|
| `kcrypto/core/contracts.py` | CONTRACT-READY | `Result` and `Finding` dataclasses implemented |
| `kcrypto/core/logger.py` | CONTRACT-READY | `make_logger` with step/found/fail/warn markers |
| `kcrypto/core/encoding.py` | SCAFFOLD | placeholder only |
| `kcrypto/core/factor.py` | SCAFFOLD | placeholder only |
| `kcrypto/core/math.py` | SCAFFOLD | placeholder only |
| `kcrypto/core/__init__.py` | SCAFFOLD | package placeholder |

## 6. Tests Snapshot (Attack/Analyze/Core-related)

| Test file | Status |
|---|---|
| `tests/core/test_contracts.py` | ACTIVE |
| `tests/core/test_logger.py` | ACTIVE |
| `tests/core/test_bridges.py` | ACTIVE |
| `tests/attacks/**` | NO ACTIVE TEST FILES YET |

Implication:

- Core baseline contracts/logging/bridges are test-covered.
- Attack and analyze layers are currently scaffold-first with minimal/no behavior coverage.

## 7. Canonical Attack Naming (Cheatsheet View)

Use one normalized attack identifier style across API, docs, tests, fixtures, and dispatcher I/O.

Canonical format:

- catalog key: `domain/action`
- both `domain` and `action` are lowercase snake_case
- recommended regex: `^[a-z][a-z0-9_]*(/[a-z][a-z0-9_]*)$`

Noun-style examples (keep stable familiar names):

- `rsa/fermat_factorization`
- `rsa/wiener_attack`
- `rsa/boneh_durfee_attack`
- `rsa/known_d_factorization`
- `rsa/known_phi_factorization`
- `factoring/smart_attack`

Suggested alias seed:

- `rsa/know_d_factor` -> `rsa/known_d_factorization`
- `rsa/known_phi` -> `rsa/known_phi_factorization`
- `rsa/fermat` -> `rsa/fermat_factorization`
- `wienner` -> `rsa/wiener_attack`
- `franklinreiter` -> `rsa/franklin_reiter_attack`
- `factoring/smart` -> `factoring/smart_attack`

## 8. Recommended Next Milestones

1. Implement and test one full end-to-end path:
	`analyze/rsa.py` -> `attacks/rsa/wiener.py` -> contract tests.
2. Add an attack-name normalization helper in dispatcher-facing code path.
3. Add attack-level test skeletons for each RSA and factoring module.
4. Expand this cheatsheet with per-module tier (`T1/T2/T3`) once modules move past scaffold.
