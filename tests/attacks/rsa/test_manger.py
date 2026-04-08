from __future__ import annotations

from kcrypto.attacks.rsa import MangerAttack

# Pre-computed RSA parameters (p=1009, q=1013, e=65537)
# n.bit_length() = 20, so B = 2^12 = 4096
_N = 1022117
_E = 65537
_D = 832193
_B = 4096
_M = 1000       # plaintext < B so oracle(c) = True initially
_C = 680282     # pow(_M, _E, _N)


def _oracle(ct: int) -> bool:
    """True when decryption < B (first byte is 0x00)."""
    return pow(ct, _D, _N) < _B


# --- Contract tests ---

def test_manger_attack_recovers_plaintext() -> None:
    attack = MangerAttack(_C, _N, _E, _oracle, B=_B)
    result = attack.run()

    assert result.success is True
    assert result.attack == "rsa/manger_attack"
    assert result.error is None
    assert result.data["plaintext"] == _M


def test_manger_attack_result_contract() -> None:
    attack = MangerAttack(_C, _N, _E, _oracle, B=_B)
    result = attack.run()

    assert result.success is True
    assert isinstance(result.elapsed, float)
    assert result.elapsed >= 0


def test_manger_attack_artifacts_contain_query_count() -> None:
    attack = MangerAttack(_C, _N, _E, _oracle, B=_B)
    result = attack.run()

    assert result.success is True
    assert "queries" in result.artifacts
    assert result.artifacts["queries"] > 0


def test_manger_attack_artifacts_contain_f1_f2() -> None:
    attack = MangerAttack(_C, _N, _E, _oracle, B=_B)
    result = attack.run()

    assert result.success is True
    assert "f1" in result.artifacts
    assert "f2" in result.artifacts


def test_manger_attack_default_B_inferred() -> None:
    """B=None should default to 2^(n.bit_length()-8) = 4096 for this n."""
    attack = MangerAttack(_C, _N, _E, _oracle)
    result = attack.run()

    assert result.success is True
    assert result.data["plaintext"] == _M


def test_manger_attack_oracle_error_returns_failure() -> None:
    def bad_oracle(ct: int) -> bool:
        raise RuntimeError("oracle exploded")

    attack = MangerAttack(_C, _N, _E, bad_oracle, B=_B)
    result = attack.run()

    assert result.success is False
    assert result.attack == "rsa/manger_attack"
    assert result.error is not None


def test_manger_attack_verbose_does_not_crash() -> None:
    attack = MangerAttack(_C, _N, _E, _oracle, B=_B, verbose=True)
    result = attack.run()

    assert result.success is True
