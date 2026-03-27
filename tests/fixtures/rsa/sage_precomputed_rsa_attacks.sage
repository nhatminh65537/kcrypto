import json
import sage.all as sa


sa.set_random_seed(20260327)


def next_prime_from(n):
    return int(sa.next_prime(sa.Integer(n)))


p_w = next_prime_from(2**511 + 123456789)
q_w = next_prime_from(2**513 + 987654321)
N_w = p_w * q_w
phi_w = (p_w - 1) * (q_w - 1)
d_w = 5
while sa.gcd(d_w, phi_w) != 1:
    d_w += 2
e_w = int(sa.inverse_mod(d_w, phi_w))
m_w = int(2**200 + 1337)
c_w = int(pow(m_w, e_w, N_w))

base_f = sa.Integer(2**512 + 5555555)
p_f = next_prime_from(base_f)
q_f = next_prime_from(p_f + 120)
if q_f % 2 == 0:
    q_f = next_prime_from(q_f + 1)
N_f = int(p_f * q_f)
a_f = int((p_f + q_f) // 2)
b_f = int((q_f - p_f) // 2)

p_d = next_prime_from(2**513 + 7777777)
q_d = next_prime_from(2**511 + 2222222)
N_d = int(p_d * q_d)
phi_d = int((p_d - 1) * (q_d - 1))
e_d = 65537
if sa.gcd(e_d, phi_d) != 1:
    e_d = int(sa.next_prime(e_d))
d_d = int(sa.inverse_mod(e_d, phi_d))

p_phi = next_prime_from(2**512 + 3333333)
q_phi = next_prime_from(2**511 + 9999999)
N_phi = int(p_phi * q_phi)
phi_phi = int((p_phi - 1) * (q_phi - 1))

cases = {
    "wiener": {
        "inputs": {"N": int(N_w), "e": int(e_w), "c": int(c_w)},
        "expected": {
            "p": int(p_w),
            "q": int(q_w),
            "phi": int(phi_w),
            "d": int(d_w),
            "m": int(m_w),
        },
    },
    "fermat_factorization": {
        "inputs": {"N": int(N_f), "max_iterations": 1000000},
        "expected": {
            "p": int(p_f),
            "q": int(q_f),
            "a": int(a_f),
            "b": int(b_f),
            "iterations": int(b_f + 1),
        },
    },
    "known_d_factorization": {
        "inputs": {"N": int(N_d), "e": int(e_d), "d": int(d_d)},
        "expected": {"p": int(p_d), "q": int(q_d), "phi": int(phi_d)},
    },
    "known_phi_factorization": {
        "inputs": {"N": int(N_phi), "phi": int(phi_phi)},
        "expected": {
            "p": int(p_phi),
            "q": int(q_phi),
            "sum_pq": int(p_phi + q_phi),
        },
    },
}

payload = {
    "generated_with": "SageMath",
    "generated_at": "2026-03-27",
    "notes": "Precomputed expected values for RSA attack skeleton tests.",
    "cases": cases,
}

print(json.dumps(payload, indent=2))
