"""Küçük LeRobot datasetinde episode sınırını aşmayan action chunk/padding deneyi."""
import argparse
import json
from pathlib import Path

import numpy as np


def build_windows(rows, horizon):
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError("horizon pozitif tam sayı olmalı")
    groups = {}
    for row in rows:
        groups.setdefault(row["episode_index"], []).append(row)
    chunks, pads, episode_ids, frame_ids, states = [], [], [], [], []
    for episode, frames in sorted(groups.items()):
        frames.sort(key=lambda r: r["frame_index"])
        if [f["frame_index"] for f in frames] != list(range(len(frames))):
            raise ValueError(f"episode {episode}: frame sırası eksik/tekrarlı")
        actions = np.asarray([r["action"] for r in frames], dtype=np.float32)
        observations = np.asarray([r["observation.state"] for r in frames], dtype=np.float32)
        if actions.ndim != 2 or observations.ndim != 2 or not actions.shape[1]:
            raise ValueError("state/action birer vektör olmalı")
        if not np.isfinite(actions).all() or not np.isfinite(observations).all():
            raise ValueError("NaN/Inf veri")
        for i, frame in enumerate(frames):
            indices = i + np.arange(horizon)
            is_pad = indices >= len(frames)
            chunks.append(actions[np.minimum(indices, len(frames) - 1)])
            pads.append(is_pad)
            states.append(observations[i])
            episode_ids.append(episode)
            frame_ids.append(frame["frame_index"])
    if not chunks:
        raise ValueError("Veri boş")
    return {"actions": np.stack(chunks), "action_is_pad": np.stack(pads),
            "states": np.stack(states), "episode_index": np.array(episode_ids),
            "frame_index": np.array(frame_ids)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--horizon", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("outputs/action-windows.npz"))
    parser.add_argument("--verify-lerobot", action="store_true",
                        help="Episode uçlarındaki action/maskeyi gerçek LeRobot okuyucusuyla karşılaştır")
    args = parser.parse_args()
    if not 1 <= args.horizon <= 1000:
        parser.error("horizon 1–1000 olmalı")
    if args.output.exists():
        parser.error("Çıktı mevcut; yeni --output seç")
    import pyarrow.parquet as pq
    rows = []
    for file in sorted((args.root / "data").rglob("*.parquet")):
        rows.extend(pq.read_table(file, columns=["episode_index", "frame_index",
                                               "observation.state", "action"]).to_pylist())
    arrays = build_windows(rows, args.horizon)
    compared = 0
    if args.verify_lerobot:
        from common import prepare_paths
        prepare_paths()
        from lerobot.datasets.lerobot_dataset import LeRobotDataset
        info = json.loads((args.root / "meta/info.json").read_text())
        dataset = LeRobotDataset("local/window-check", root=args.root.resolve(),
                                 video_backend="pyav",
                                 delta_timestamps={"action": [i / info["fps"] for i in range(args.horizon)]})
        if len(dataset) != len(arrays["episode_index"]):
            raise ValueError("LeRobot ve pencere örnek sayısı farklı")
        for episode in np.unique(arrays["episode_index"]):
            indices = np.flatnonzero(arrays["episode_index"] == episode)
            for index in sorted(set([int(indices[0]), int(indices[-1])])):
                frame = dataset[index]
                if int(frame["episode_index"]) != int(episode) or int(frame["frame_index"]) != int(arrays["frame_index"][index]):
                    raise ValueError("LeRobot okuyucu sırası bu öğretim örneğiyle uyuşmuyor")
                np.testing.assert_allclose(frame["action"].numpy(), arrays["actions"][index])
                np.testing.assert_array_equal(frame["action_is_pad"].numpy(), arrays["action_is_pad"][index])
                compared += 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as f:
        np.savez_compressed(f, **arrays)
    info = {"shapes": {k: list(v.shape) for k, v in arrays.items()},
            "padded_fraction": float(arrays["action_is_pad"].mean()),
            "first_valid_steps": int((~arrays["action_is_pad"][0]).sum()),
            "last_valid_steps": int((~arrays["action_is_pad"][-1]).sum()),
            "lerobot_boundary_samples_verified": compared,
            "output": str(args.output),
            "scope": "Educational windows; no normalization or training-loader replacement. Verification also reads boundary video frames."}
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
