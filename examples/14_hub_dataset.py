"""Inspect a public Hub dataset, preview metadata or download a size-limited pinned snapshot."""
import argparse
from fnmatch import fnmatch
import json
from pathlib import Path

from common import prepare_paths


def select_files(files, metadata_only):
    selected = []
    for item in files:
        if not hasattr(item, "size"):
            continue
        if not metadata_only or fnmatch(item.path, "meta/*") or item.path == "README.md":
            selected.append(item)
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_id", help="Owner/dataset, NOT a model repository")
    parser.add_argument("--revision", default="main")
    parser.add_argument("--mode", choices=["inspect", "metadata", "download"], default="inspect")
    parser.add_argument("--root", type=Path)
    parser.add_argument("--max-mb", type=float, default=250, help="Download ceiling in decimal MB")
    args = parser.parse_args()
    if args.mode != "inspect" and args.root is None:
        parser.error("metadata/download require --root")
    if not 0 < args.max_mb < float("inf"):
        parser.error("max-mb must be finite and positive")
    if args.mode != "inspect" and args.root.exists():
        parser.error("Root already exists; use a fresh directory")
    prepare_paths()
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download
    api = HfApi()
    repo = api.dataset_info(args.repo_id, revision=args.revision)
    revision = repo.sha
    files = list(api.list_repo_tree(args.repo_id, repo_type="dataset", revision=revision, recursive=True))
    selected = select_files(files, metadata_only=args.mode != "download")
    full = select_files(files, metadata_only=False)
    report = {"repo_id": args.repo_id, "revision": revision, "mode": args.mode,
              "all_files": len(full), "total_mb": sum(f.size for f in full) / 1e6,
              "selected_files": len(selected), "selected_mb": sum(f.size for f in selected) / 1e6,
              "license": (repo.card_data or {}).get("license")}
    info_entry = next((f for f in full if f.path == "meta/info.json"), None)
    if info_entry is not None and info_entry.size <= 2_000_000:
        path = hf_hub_download(args.repo_id, "meta/info.json", repo_type="dataset", revision=revision)
        info = json.loads(Path(path).read_text())
        report["lerobot"] = {k: info.get(k) for k in ["codebase_version", "robot_type", "fps", "total_episodes", "total_frames", "features"]}
    else:
        report["lerobot"] = "No small meta/info.json; inspect the dataset format before using LeRobot"
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    if args.mode == "inspect":
        print("Inspection only: repository listing and at most meta/info.json were fetched.")
        return
    if not selected:
        parser.error("No matching files")
    if report["selected_mb"] > args.max_mb:
        parser.error(f"Selected {report['selected_mb']:.2f} MB exceeds --max-mb={args.max_mb}; no snapshot downloaded")
    snapshot_download(args.repo_id, repo_type="dataset", revision=revision,
                      allow_patterns=[f.path for f in selected], local_dir=args.root)
    (args.root / "ATOLYE_DOWNLOAD.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    print(f"Saved {args.mode} snapshot: {args.root}")
    if args.mode == "metadata":
        print("Metadata preview is NOT a trainable complete dataset.")


if __name__ == "__main__":
    main()
