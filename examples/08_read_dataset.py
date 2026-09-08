"""Yerel LeRobot verisini PyAV ile okur; ilk kamerayı PNG'ye çıkarır."""
import argparse
import json
from pathlib import Path
from common import ROOT, prepare_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--index", type=int, default=0)
    args = parser.parse_args()
    if not (args.root / "meta/info.json").is_file():
        parser.error("Yerel meta/info.json yok; bu script otomatik dataset indirmez")
    prepare_paths()
    import numpy as np
    from PIL import Image
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    dataset = LeRobotDataset(args.repo_id, root=args.root.resolve(), video_backend="pyav")
    if not 0 <= args.index < len(dataset):
        parser.error(f"index 0–{len(dataset)-1} arasında olmalı")
    frame = dataset[args.index]
    cameras = [key for key in frame if key.startswith("observation.images.")]
    if not cameras:
        parser.error("Frame içinde kamera yok")
    report = {"frames": len(dataset), "index": args.index, "keys": sorted(frame), "shapes": {}}
    for key in cameras:
        array = frame[key].detach().cpu().numpy()
        if array.ndim != 3 or array.shape[0] != 3 or not np.isfinite(array).all():
            raise ValueError(f"Geçersiz görüntü tensörü: {key}")
        report["shapes"][key] = list(array.shape)
        name = key.removeprefix("observation.images.").replace("/", "_").replace("\\", "_")
        path = ROOT / "outputs" / f"dataset_frame_{args.index}_{name}.png"
        Image.fromarray((array.transpose(1, 2, 0).clip(0, 1)*255).astype(np.uint8)).save(path)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("Kamera PNG dosyaları outputs/ altında. Bir frame bütün episode kalitesini kanıtlamaz.")


if __name__ == "__main__":
    main()
