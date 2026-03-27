"""Recover RSA private key material with Wiener's attack (Tier 1)."""

from __future__ import annotations

from time import perf_counter

from kcrypto.core.contracts import Result
from kcrypto.core.logger import make_logger
from kcrypto.bridges.sage import sage as sg
from kcrypto.attacks.rsa.known_phi_factorization import known_phi_factorization


TIER = "T1"
ATTACK_KEY = "rsa/wiener_attack"


def wiener_attack(e: int, N: int, c: int | None = None, verbose: bool = False) -> Result:
	"""Run Wiener's continued-fraction attack against an RSA public key.

	Tier:
		T1 (pure function).

	Applicability:
		Best suited for weak RSA keys where private exponent ``d`` is small.

	Failure Mode:
		Returns ``Result(success=False, error=...)`` for invalid input or when no
		valid convergent yields non-trivial factors.

	Success Data Keys:
		d: Recovered private exponent candidate.
		p: First recovered prime factor.
		q: Second recovered prime factor.
		sum_pq: Sum ``p + q`` inferred during factor recovery.

	Args:
		e: RSA public exponent.
		N: RSA modulus.
		c: Optional ciphertext. Reserved for future plaintext recovery output.
		verbose: If True, emit checkpoint logs.

	Returns:
		Result contract containing attack status, outputs, and metadata.
	"""
	started = perf_counter()
	log = make_logger("wiener_attack", verbose)
	log("validate inputs")

	if e <= 1 or N <= 1:
		elapsed_ms = (perf_counter() - started) * 1000.0
		log.fail("e and N must be integers greater than 1")
		return Result(
			success=False,
			attack=ATTACK_KEY,
			data={},
			artifacts={"tier": TIER, "inputs": {"e": e, "N": N, "c": c}},
			error="e and N must be integers greater than 1.",
			elapsed=elapsed_ms,
		)

	cf = sg.continued_fraction(sg.ZZ(e) / sg.ZZ(N))

	for convergent in cf.convergents():
		k = convergent.numerator()
		d = convergent.denominator()

		if k == 0:
			continue

		if (e * d - 1) % k != 0:
			continue

		phi = (e * d - 1) // k
		result = known_phi_factorization(N, phi, verbose=verbose)
		if result.success:
			log.found("Wiener's attack successful")
			return Result(
				success=True,
				attack=ATTACK_KEY,
				data={"d": d, **result.data},
				artifacts={"tier": TIER, "inputs": {"e": e, "N": N, "c": c}},
				error=None,
				elapsed=(perf_counter() - started) * 1000.0,
			)
	
	elapsed_ms = (perf_counter() - started) * 1000.0
	log.fail("Wiener's attack failed to find valid d")
	return Result(
		success=False,
		attack=ATTACK_KEY,
		data={},
		artifacts={"tier": TIER, "inputs": {"e": e, "N": N, "c": c}},
		error="Wiener's attack failed to find valid d",
		elapsed=elapsed_ms,
	)