"""Convert the first-learning CSV into a local numeric LeRobot dataset; no upload or invented images."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from common import prepare_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    if args.root.exists():
        parser.error("Choose a new root")
    with args.csv.open(newline="") as f:
        rows = list(csv.DictReader(f))
    groups = {}
    for row in rows:
        ep = int(row["episode"])
        values = np.array([float(row[k]) for k in ["q_rad", "goal_rad", "action_rad"]])
        if not np.isfinite(values).all():
            parser.error("Non-finite source data")
        groups.setdefault(ep, []).append(row)
    if not groups:
        parser.error("Empty CSV")
    if sorted(groups) != list(range(len(groups))):
        parser.error("Source episode IDs must be consecutive from zero")
    for ep, frames in groups.items():
        frames.sort(key=lambda r: int(r["frame"]))
        if [int(r["frame"]) for r in frames] != list(range(len(frames))):
            parser.error(f"Episode {ep} has a frame gap/duplicate")
        if len({r["split"] for r in frames}) != 1:
            parser.error(f"Episode {ep} crosses splits")
    prepare_paths()
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    dataset = LeRobotDataset.create(repo_id="local/teaching-hinge", root=args.root.resolve(), fps=50,
        robot_type="teaching_hinge", use_videos=False, features={
            "observation.state": {"dtype": "float32", "shape": (2,), "names": ["pan_rad", "goal_rad"]},
            "action": {"dtype": "float32", "shape": (1,), "names": ["pan_target_rad"]},
        })
    splits = {}
    for ep, frames in sorted(groups.items()):
        splits[str(ep)] = frames[0]["split"]
        for row in frames:
            dataset.add_frame({"observation.state": np.array([float(row["q_rad"]), float(row["goal_rad"])], dtype=np.float32),
                               "action": np.array([float(row["action_rad"])], dtype=np.float32),
                               "task": "Reach the target hinge angle"})
        dataset.save_episode()
    dataset.finalize()
    (args.root / "ATOLYE_CARD.json").write_text(json.dumps({
        "source_csv": str(args.csv.resolve()), "units": "radians", "observation_includes_goal": True,
        "action_semantics": "absolute position target", "episodes_split": splits,
        "purpose": "numeric format/learning exercise; not an SO101 or SmolVLA image dataset",
    }, indent=2))
    print(json.dumps({"episodes": len(groups), "frames": len(rows), "root": str(args.root),
                      "uploaded": False, "cameras": 0}, indent=2))


if __name__ == "__main__":
    main()
