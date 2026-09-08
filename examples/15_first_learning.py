"""Generate MuJoCo demonstrations, train a tiny CPU policy, then run held-out physics episodes."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/first-learning")
    parser.add_argument("--steps", type=int, default=1500, help="Optimizer updates")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a fresh --output")
    if not 1 <= args.steps <= 10000:
        parser.error("steps must be 1–10000")
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    module_spec = importlib.util.spec_from_file_location("playground", ROOT / "examples/13_mujoco_playground.py")
    playground = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(playground)
    model, data = playground.make_scene("servo")
    q_index = model.jnt_qposadr[model.joint("pan").id]
    actuator = model.actuator("pan_target").id

    def reset(start):
        mujoco.mj_resetData(model, data)
        data.qpos[q_index] = start
        mujoco.mj_forward(model, data)

    def step(command):
        data.ctrl[actuator] = np.clip(command, -1.5, 1.5)
        for _ in range(10):
            mujoco.mj_step(model, data)

    # Entire episodes are assigned to train, validation and test BEFORE sampling frames.
    settings = [(float(rng.uniform(-.9, .9)), float(rng.uniform(-.9, .9))) for _ in range(40)]
    samples = []
    for ep, (start, goal) in enumerate(settings):
        reset(start)
        split = "train" if ep < 28 else "validation" if ep < 34 else "test"
        for frame in range(100):
            q = float(data.qpos[q_index])
            action = q + np.clip(goal - q, -.06, .06)
            samples.append({"episode": ep, "frame": frame, "split": split,
                            "q_rad": q, "goal_rad": goal, "action_rad": float(action)})
            step(action)
    x = np.array([[r["q_rad"], r["goal_rad"]] for r in samples], dtype=np.float32)
    y = np.array([[r["action_rad"]] for r in samples], dtype=np.float32)
    train = np.array([r["split"] == "train" for r in samples])
    val = np.array([r["split"] == "validation" for r in samples])
    mean, std = x[train].mean(0), x[train].std(0).clip(1e-6)
    features = torch.tensor((x - mean) / std)
    labels = torch.tensor(y)
    train_ids = np.flatnonzero(train)
    policy = torch.nn.Sequential(torch.nn.Linear(2, 32), torch.nn.Tanh(),
                                 torch.nn.Linear(32, 32), torch.nn.Tanh(), torch.nn.Linear(32, 1))
    optimizer = torch.optim.Adam(policy.parameters(), lr=.003)
    history, best, best_state = [], float("inf"), None
    for update in range(1, args.steps + 1):
        ids = rng.choice(train_ids, size=128, replace=True)
        predicted = policy(features[ids])
        loss = torch.nn.functional.mse_loss(predicted, labels[ids])
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if update % 100 == 0 or update == args.steps:
            with torch.no_grad():
                val_loss = float(torch.nn.functional.mse_loss(policy(features[val]), labels[val]))
            history.append([update, float(loss.detach()), val_loss])
            if val_loss < best:
                best = val_loss
                best_state = {k: v.detach().clone() for k, v in policy.state_dict().items()}
    policy.load_state_dict(best_state)
    policy.eval()
    outcomes = []
    for ep in range(34, 40):
        start, goal = settings[ep]
        for name in ["learned", "hold_start"]:
            reset(start)
            for _ in range(100):
                if name == "hold_start":
                    command = start
                else:
                    observation = np.array([float(data.qpos[q_index]), goal], dtype=np.float32)
                    with torch.no_grad():
                        command = float(policy(torch.tensor((observation - mean) / std)).item())
                step(command)
            error = abs(float(data.qpos[q_index]) - goal)
            outcomes.append({"episode": ep, "policy": name, "start_rad": start, "goal_rad": goal,
                             "final_error_rad": error, "success": error < .04})
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "demonstrations.csv").open("x", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    np.savez_compressed(args.output / "training_arrays.npz", observations=x, actions=y,
                        train_mask=train, validation_mask=val, mean=mean, std=std)
    torch.save({"state_dict": policy.state_dict(), "mean": mean.tolist(), "std": std.tolist(),
                "architecture": "Linear(2,32),Tanh,Linear(32,32),Tanh,Linear(32,1)"}, args.output / "policy.pt")
    np.savetxt(args.output / "loss.csv", history, delimiter=",", header="update,train_batch_mse,validation_mse", comments="")
    report = {"seed": args.seed, "optimizer_updates": args.steps, "control_hz": 50,
              "train_episodes": 28, "validation_episodes": 6, "test_episodes": 6,
              "demonstration_frames": len(samples), "best_validation_mse": best,
              "rollouts": outcomes, "scope": "One simulated hinge, state+goal input, CPU MLP. No images, language, SO101 or VLA."}
    for name in ["learned", "hold_start"]:
        group = [r for r in outcomes if r["policy"] == name]
        report[name] = {"successes": sum(r["success"] for r in group), "trials": len(group),
                        "mean_final_error_rad": float(np.mean([r["final_error_rad"] for r in group]))}
    (args.output / "metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
