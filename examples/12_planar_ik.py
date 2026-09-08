"""İki eklemli düzlemsel kol: iki analitik IK çözümü, FK ve Jacobian denetimi."""
import argparse
import json
import math
import numpy as np

L1, L2 = .18, .14


def fk(q):
    a, b = q
    return np.array([L1 * np.cos(a) + L2 * np.cos(a + b),
                     L1 * np.sin(a) + L2 * np.sin(a + b)])


def jacobian(q):
    a, b = q
    return np.array([[-L1*np.sin(a)-L2*np.sin(a+b), -L2*np.sin(a+b)],
                     [L1*np.cos(a)+L2*np.cos(a+b), L2*np.cos(a+b)]])


def ik(x, y):
    if not math.isfinite(x) or not math.isfinite(y):
        raise ValueError("Hedef sonlu olmalı")
    c = (x*x + y*y - L1*L1 - L2*L2) / (2*L1*L2)
    if abs(c) > 1 + 1e-12:
        raise ValueError("Hedef erişim halkası dışında: 0.04 <= r <= 0.32 m")
    c = float(np.clip(c, -1, 1))
    solutions = []
    for sign in [1, -1]:
        b = sign * math.acos(c)
        a = math.atan2(y, x) - math.atan2(L2*math.sin(b), L1+L2*math.cos(b))
        solutions.append(np.array([a, b]))
    return solutions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--x", type=float, default=.22, help="metre")
    parser.add_argument("--y", type=float, default=.10, help="metre")
    args = parser.parse_args()
    try:
        solutions = ik(args.x, args.y)
    except ValueError as exc:
        parser.exit(1, str(exc) + "\n")
    report = []
    for q in solutions:
        numerical = np.column_stack([(fk(q + np.eye(2)[i]*1e-6) -
                                       fk(q - np.eye(2)[i]*1e-6)) / 2e-6 for i in range(2)])
        np.testing.assert_allclose(jacobian(q), numerical, atol=1e-9)
        np.testing.assert_allclose(fk(q), [args.x, args.y], atol=1e-12)
        report.append({"q_rad": q.tolist(), "q_deg": np.rad2deg(q).tolist(),
                       "fk_m": fk(q).tolist(), "jacobian_m_per_rad": jacobian(q).tolist(),
                       "singular_values": np.linalg.svd(jacobian(q), compute_uv=False).tolist()})
    print(json.dumps({"target_m": [args.x, args.y], "solutions": report,
                      "scope": "Ideal 2R planar arm; no joint limits, collision or SO101 IK"}, indent=2))


if __name__ == "__main__":
    main()
