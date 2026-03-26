# AGENTS.md — kcrypto

> **Đọc file này trước khi làm bất cứ điều gì.** Đây là source of truth về quy ước, workflow, và phân công giữa Agent và Human trong project này.

---

## 1. Tổng quan project

`kcrypto` là Python library tổng hợp crypto attacks cho CTF và security research.

- **Ngôn ngữ:** Python 3.11+
- **Test runner:** pytest
- **Doc style:** Google-style docstrings
- **Optional deps:** Sage (`kcrypto[sage]`), z3 (`kcrypto[z3]`), pwntools (`kcrypto[pwn]`)
- **Package root:** `kcrypto/`
- **Trạng thái hiện tại:** skeleton-first, nhiều module đang ở scaffold phase

---

## 2. Phân chia trách nhiệm — QUAN TRỌNG

| Việc | Người làm | Ghi chú |
|------|-----------|---------|
| Scaffold file, skeleton class/function | Agent | Đúng naming, đúng tier |
| Viết/chuẩn hóa docstring | Agent | Google style, rõ constraints |
| Wrap output vào `Result` / `Finding` | Agent | Theo contract cứng |
| Hook logger vào checkpoints | Agent | Không bỏ sót đường fail |
| Viết test skeleton + fixture plumbing | Agent | Có thể để TODO nếu thiếu expected Sage |
| Chạy pytest và báo kết quả | Agent | Gate bắt buộc trước khi kết luận |
| Cập nhật AGENTS nếu đổi public contract | Agent | Top-level hoặc per-module |
| **Core crypto algorithm logic** | **Human** | Agent KHÔNG tự điền phần toán học chính |
| **Private helper có crypto math trọng yếu** | **Human** | Agent để `# TODO: implement` hoặc `raise NotImplementedError("Human implements")` |
| Review algorithm correctness | Human | |
| Merge PR / publish release | Human | |

> **Nguyên tắc:** Agent tạo form chuẩn (API, contracts, tests, docs). Human điền content toán học lõi.

---

## 3. 3-Tier Attack System

### Tier 1 — Pure Function

```python
def wiener(e: int, N: int, c: int | None = None, verbose: bool = False) -> Result:
    """..."""
    log = make_logger("wiener", verbose)
    # TODO: implement attack math
    raise NotImplementedError("Human implements")
```

- Không cần state inspect qua nhiều step
- Input -> output trực tiếp

### Tier 2 — Stateful Object

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

- Params lock tại `__init__`
- State tích lũy qua steps
- Mỗi step nên return `self` để chain (khi phù hợp)

### Tier 3 — Oracle-based Object

- Giống Tier 2, thêm external oracle/callback nhận ở `__init__`
- Ưu tiên inject oracle rõ kiểu dữ liệu
- Không gộp nhiều tier khác bản chất vào cùng một class

---

## 4. Contracts cốt lõi

### 4.1 Attack outputs

- Dynamic attack APIs trả về `Result`
- Analyze APIs trả về `Finding` hoặc `list[Finding]`
- Normal failure path phải encode trong `Result(success=False, error=...)`, không throw exception cho case expected

### 4.2 Logger

- Dùng thống nhất qua `make_logger("attack_name", verbose)`
- Checkpoint nên có: progress, found, fail

### 4.3 Interface stability

- Không đổi public signature khi chưa có yêu cầu rõ ràng
- Nếu buộc đổi contract: cập nhật tests + docs + AGENTS cùng lúc

---

## 5. Rules bắt buộc

### 5.1 Factoring rule

- **KHÔNG BAO GIỜ** gọi `sage.factor(...)` trực tiếp trong attack flow ngoài phạm vi factoring module
- Khi cần factor trong attack khác, đi qua factoring dispatcher/API của package

### 5.2 Optional dependencies

- Core import phải chạy dù không cài Sage/z3/pwn
- Lazy import optional deps, fail message phải rõ cách cài extra

### 5.3 Docstring

- Public function/class trong `kcrypto/attacks/` và `kcrypto/analyze/` phải có Google-style docstring
- Docstring mô tả rõ điều kiện áp dụng, fail mode, key trong `data`

### 5.4 Tests

- Mỗi attack tối thiểu: success case + failure case + edge case
- Nếu fixture cần số liệu Sage, lưu script/cách generate để tái lập

### 5.5 AGENTS sync

- Khi thêm/sửa public symbol hoặc behavior contract: update AGENTS liên quan ngay trong cùng task

---

## 6. Skill workflow trong repo này

Skills nằm ở `.github/skills/`.

| Skill | Khi nào dùng |
|-------|-------------|
| `kcrypto-conventions` | Khi sửa trong `kcrypto/attacks/`, `kcrypto/analyze/`, hoặc đổi contract kiến trúc |
| `test-driven-development` | Trước khi implement feature/bugfix |
| `systematic-debugging` | Khi test fail hoặc behavior sai kỳ vọng |
| `writing-plans` | Khi task nhiều bước hoặc cần execution plan rõ ràng |
| `verification-before-completion` | Trước khi kết luận task đã xong |
| `requesting-code-review` | Trước mốc merge nếu thay đổi lớn |
| `finishing-a-development-branch` | Sau khi pass verify và chuẩn bị integrate |

### Attack implementation loop (tóm tắt)

```
Agent: tạo skeleton + test skeleton/fixture plumbing
    ↓
Human: điền crypto algorithm core vào TODO blocks
    ↓
Agent: complete glue (Result/Finding wrap, logger hooks, timing)
    ↓
Agent: pytest + verify contract
    ↓ [fail] -> isolate: lỗi glue -> Agent fix | lỗi algorithm -> Human fix
    ↓ [pass]
Tiếp module/attack tiếp theo
```

---

## 7. OpenMemory MCP

Project dùng OpenMemory để giữ context qua sessions. Agent cần:

- Trước session: load memory liên quan phase/batch/quyết định đã chốt
- Sau milestone: lưu metadata ngắn gọn (status, tier, decision), không lưu data lớn

Format khuyến nghị:

```
kcrypto | kcrypto/attacks/rsa/wiener.py | status: done | tier: T1 | verify: pytest-pass
kcrypto | phase: scaffold | module: rsa | next: hastad skeleton
kcrypto | decision: keep factoring dispatcher as single entrypoint
```

---

## 8. Directory layout (thực tế)

```
AGENTS.md
pyproject.toml
README.md
docs/
kcrypto/
  __init__.py
  _logger.py
  _result.py
  analyze/
  attacks/
  bridges/
  core/
tests/
  attacks/
  fixtures/
```

Ghi chú:

- Attack modules nằm trong `kcrypto/attacks/<domain>/`
- Analyze modules nằm trong `kcrypto/analyze/`
- Bridge optional deps nằm trong `kcrypto/bridges/`

---

## 9. Những điều Agent KHÔNG được làm

- Tự điền crypto algorithm lõi vào TODO blocks mà Human chưa duyệt
- Thay đổi public contract ngầm (signature, kiểu output, key data) mà không cập nhật docs/tests
- Gọi trực tiếp API phá kiến trúc factoring dispatcher trong attack flow
- Báo xong khi chưa chạy verify phù hợp (ít nhất pytest cho phạm vi thay đổi)
- Commit thẳng vào `main` khi chưa có yêu cầu explicit

---

## 10. Definition of done cho một attack/module

- API skeleton hoặc implementation đúng tier
- `Result`/`Finding` contract đúng
- Logger checkpoints hợp lý
- Tests liên quan đã thêm/chạy
- Docs và AGENTS sync với behavior mới