"""LeRobot v3 metadata/parquet denetimi; görüntüler ayrıca görsel olarak incelenmeli."""
import argparse
import json
from pathlib import Path


def inspect_dataset(root: Path, expected_episodes=None):
    import numpy as np
    import pyarrow.parquet as pq
    info = json.loads((root / "meta/info.json").read_text())
    paths = sorted((root / "data").rglob("*.parquet"))
    if not paths:
        raise ValueError("data/ altında parquet bulunamadı")
    rows = []
    for path in paths:
        rows.extend(pq.read_table(path, columns=["episode_index", "frame_index", "timestamp",
                                               "observation.state", "action"]).to_pylist())
    groups = {}
    errors = []
    fps = info["fps"]
    if not isinstance(fps, (int, float)) or not np.isfinite(fps) or fps <= 0:
        raise ValueError("metadata fps sonlu ve pozitif olmalı")
    for row in rows:
        groups.setdefault(row["episode_index"], []).append(row)
        for key in ("observation.state", "action"):
            values = np.asarray(row[key], dtype=float)
            expected_shape = tuple(info["features"][key]["shape"])
            # LeRobot stores length-one numeric features as Parquet scalars.
            # Accept that storage form only for a declared length-one feature.
            if expected_shape == (1,) and values.shape == ():
                values = values.reshape(1)
            if values.shape != expected_shape or not np.isfinite(values).all():
                errors.append(f"episode {row['episode_index']} frame {row['frame_index']}: {key} şekil/NaN hatası")
    for index, frames in groups.items():
        frames.sort(key=lambda f: f["frame_index"])
        if [f["frame_index"] for f in frames] != list(range(len(frames))):
            errors.append(f"episode {index}: frame_index atlaması/tekrarı")
        times = np.asarray([f["timestamp"] for f in frames])
        if not np.allclose(times, np.arange(len(frames)) / fps, atol=1e-4):
            errors.append(f"episode {index}: timestamp/FPS uyumsuzluğu")
    if info["total_frames"] != len(rows) or info["total_episodes"] != len(groups):
        errors.append("meta/info.json sayıları gerçek parquet ile uyuşmuyor")
    if expected_episodes is not None and expected_episodes != len(groups):
        errors.append(f"Beklenen {expected_episodes}, bulunan {len(groups)} episode")
    cameras = [k for k in info["features"] if k.startswith("observation.images.")]
    return {"episodes": len(groups), "frames": len(rows), "fps": fps,
            "episode_lengths": {str(k): len(v) for k, v in groups.items()},
            "camera_features": cameras, "errors": errors,
            "limits": "Video decode, uzman kalitesi, başarı ve state/action birimleri bu kontrolle kanıtlanmaz."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--expected-episodes", type=int)
    args = parser.parse_args()
    try:
        report = inspect_dataset(args.root, args.expected_episodes)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Veri denetimi başarısız: {exc}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(bool(report["errors"]))


if __name__ == "__main__":
    main()
