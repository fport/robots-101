"""python examples/00_doctor.py — salt okunur ortam raporu."""
import importlib.util
import importlib.metadata
import json
import platform
import shutil
import sys
from pathlib import Path


def main():
    versions = {}
    for package in ("mkdocs", "mkdocs-material", "strands-robots", "mujoco", "lerobot", "torch", "torchcodec"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    report = {
        "python": sys.version.split()[0], "executable": sys.executable,
        "platform": platform.platform(), "architecture": platform.machine(),
        "packages": versions, "ffmpeg": shutil.which("ffmpeg"),
        "note": "Donanıma, kameraya veya model ağırlıklarına erişilmedi.",
    }
    if importlib.util.find_spec("torch"):
        import torch
        report["accelerators"] = {"cuda": torch.cuda.is_available(), "mps": torch.backends.mps.is_available()}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if sys.version_info[:2] != (3, 12):
        print("Rehberin referans ortamı Python 3.12; sürüm farkını not et.")


if __name__ == "__main__":
    main()
