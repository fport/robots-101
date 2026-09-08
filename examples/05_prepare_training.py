"""Yerel LeRobot metadata'sından ACT/SmolVLA komutu üretir; eğitim başlatmaz."""
import argparse
import json
import re
import shlex
from pathlib import Path


def policy_features(info):
    features = info["features"]
    for key in ("observation.state", "action"):
        if features[key]["shape"] != [6]:
            raise ValueError(f"Bu SO-101 tarifi {key}=[6] bekler; bulunan {features[key]['shape']}")
    result = {"observation.state": {"type": "STATE", "shape": [6]}}
    for key, feature in features.items():
        if not key.startswith("observation.images."):
            continue
        shape = list(feature["shape"])
        names = feature.get("names", [])
        if isinstance(names, list) and all(n in names for n in ["height", "width", "channels"]):
            shape = [shape[names.index(n)] for n in ["channels", "height", "width"]]
        elif len(shape) == 3 and shape[-1] == 3:
            shape = [shape[2], shape[0], shape[1]]
        if len(shape) != 3 or shape[0] != 3 or any(n <= 0 for n in shape):
            raise ValueError(f"RGB kamera şekli çözülemedi: {key}={feature}")
        result[key] = {"type": "VISUAL", "shape": shape}
    if len(result) < 2:
        raise ValueError("En az bir RGB kamera gerekir; state-only veri VLA görsel deneyi değildir")
    return result


def make_command(info, root, repo_id, output_dir, policy="smolvla", device="cuda", steps=20000,
                 batch_size=8, eval_split=0.2):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_id):
        raise ValueError("repo-id owner/name biçiminde olmalı")
    if steps < 1 or batch_size < 1 or not 0 <= eval_split < 1:
        raise ValueError("steps/batch-size pozitif, eval-split [0,1) aralığında olmalı")
    if not isinstance(info.get("total_episodes"), int) or info["total_episodes"] < 1:
        raise ValueError("Kaydedilmiş episode bulunamadı")
    if eval_split and (info["total_episodes"] * eval_split < 1 or info["total_episodes"] * (1-eval_split) < 1):
        raise ValueError("Bu split için yeterli episode yok; daha fazla veri veya smoke için --eval-split 0 kullan")
    features = policy_features(info)
    command = ["lerobot-train", f"--dataset.repo_id={repo_id}", f"--dataset.root={root}",
               "--dataset.video_backend=pyav", f"--dataset.eval_split={eval_split}",
               f"--output_dir={output_dir}", f"--job_name=so101_{policy}", f"--policy.device={device}",
               "--policy.push_to_hub=false", "--wandb.enable=false", f"--steps={steps}",
               f"--batch_size={batch_size}", "--num_workers=0", "--seed=42",
               f"--save_freq={min(5000, steps)}", f"--eval_steps={min(1000, steps) if eval_split else 0}"]
    if policy == "smolvla":
        command.extend(["--policy.path=lerobot/smolvla_base",
                        "--policy.input_features=" + json.dumps(features, separators=(",", ":")),
                        "--policy.empty_cameras=0", "--policy.train_expert_only=true",
                        "--policy.freeze_vision_encoder=true", "--policy.train_state_proj=true"])
    elif policy == "act":
        command.append("--policy.type=act")
    else:
        raise ValueError("Yalnız act veya smolvla desteklenir")
    return command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--repo-id", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--policy", choices=["act", "smolvla"], default="smolvla")
    parser.add_argument("--device", choices=["cpu", "mps", "cuda"], default="cuda")
    parser.add_argument("--steps", type=int, default=20000)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--eval-split", type=float, default=0.2)
    parser.add_argument("--save-command", type=Path, help="İsteğe bağlı shell dosyası; mevcut dosyayı değiştirmez")
    args = parser.parse_args()
    if args.output_dir.exists():
        parser.error("output-dir zaten var; yeni eğitim için yeni yol seç. Resume ayrı bir işlemdir.")
    try:
        info = json.loads((args.root / "meta/info.json").read_text())
        command = make_command(info, str(args.root.resolve()), args.repo_id, str(args.output_dir.resolve()),
                               args.policy, args.device, args.steps, args.batch_size, args.eval_split)
        text = " \\\n  ".join(shlex.quote(arg) for arg in command) + "\n"
        if args.save_command:
            args.save_command.parent.mkdir(parents=True, exist_ok=True)
            with args.save_command.open("x") as output:
                output.write("#!/usr/bin/env bash\nset -euo pipefail\n" + text)
        print(text)
        print("# Komut üretildi. Eğitim, model indirme veya Hub yükleme başlatılmadı.")
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Eğitim hazırlığı başarısız: {exc}\n")


if __name__ == "__main__":
    main()
