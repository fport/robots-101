"""CPU'da küçük taklit öğrenme: iki eklemli FK/IK öğretmeni. SO-101 veya VLA değil."""
import argparse
import json
from pathlib import Path
import numpy as np


def fk(q):
    return np.column_stack((0.18*np.cos(q[:, 0])+0.14*np.cos(q.sum(axis=1)),
                            0.18*np.sin(q[:, 0])+0.14*np.sin(q.sum(axis=1))))


def train(steps=2000, seed=42):
    rng = np.random.default_rng(seed)
    # Tek IK dalı: aynı hedefe çelişkili dirsek çözümleri karıştırılmıyor.
    q_train = rng.uniform([0.1, 0.3], [1.6, 2.0], (1500, 2))
    q_test = rng.uniform([0.1, 0.3], [1.6, 2.0], (300, 2))
    x_train, x_test = fk(q_train), fk(q_test)
    mean, scale = x_train.mean(0), x_train.std(0)
    x = (x_train-mean)/scale
    weights = [rng.normal(0, .3, (2, 64)), np.zeros(64), rng.normal(0, .12, (64, 2)), np.zeros(2)]
    first = [np.zeros_like(p) for p in weights]
    second = [np.zeros_like(p) for p in weights]
    history = []
    for step in range(1, steps+1):
        ids = rng.integers(0, len(x), 64)
        a, y = x[ids], q_train[ids]
        w1, b1, w2, b2 = weights
        hidden = np.tanh(a@w1+b1)
        pred = hidden@w2+b2
        error = pred-y
        d_out = 2*error/error.size
        d_hidden = (d_out@w2.T)*(1-hidden**2)
        grads = [a.T@d_hidden, d_hidden.sum(0), hidden.T@d_out, d_out.sum(0)]
        for i, grad in enumerate(grads):
            first[i] = .9*first[i]+.1*grad
            second[i] = .999*second[i]+.001*grad**2
            weights[i] -= .003*(first[i]/(1-.9**step))/(np.sqrt(second[i]/(1-.999**step))+1e-8)
        if step % 100 == 0 or step == steps:
            history.append([step, float(np.mean(error**2))])
    w1, b1, w2, b2 = weights
    predicted = np.tanh(((x_test-mean)/scale)@w1+b1)@w2+b2
    errors = np.linalg.norm(fk(predicted)-x_test, axis=1)
    baseline = np.linalg.norm(fk(np.tile(q_train.mean(0), (len(q_test), 1)))-x_test, axis=1)
    report = {"task": "2D kinematic target-to-joint imitation; not SO-101/VLA",
              "train_samples": len(q_train), "test_samples": len(q_test), "steps": steps, "seed": seed,
              "mean_tip_error_cm": float(errors.mean()*100),
              "p95_tip_error_cm": float(np.quantile(errors, .95)*100),
              "fraction_under_2cm": float((errors < .02).mean()),
              "constant_baseline_error_cm": float(baseline.mean()*100)}
    return report, history, dict(w1=w1, b1=b1, w2=w2, b2=b2, mean=mean, scale=scale)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("outputs/toy-bc"))
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("steps pozitif olmalı")
    if args.output.exists():
        parser.error("Yeni çıktı klasörü seç; önceki deneyi koru")
    report, history, params = train(args.steps, args.seed)
    args.output.mkdir(parents=True)
    np.savez(args.output/"policy.npz", **params)
    np.savetxt(args.output/"loss.csv", history, delimiter=",", header="step,train_batch_mse", comments="")
    (args.output/"metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
