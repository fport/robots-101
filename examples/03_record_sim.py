"""LeRobot biçiminde 3 ayrı mock episode; yalnız veri hattını sınar."""
import argparse
import json
from pathlib import Path
from common import ROOT, checked, prepare_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT / "data/sim-smoke")
    parser.add_argument("--episodes", type=int, default=3)
    parser.add_argument("--steps", type=int, default=30)
    args = parser.parse_args()
    if args.episodes < 1 or args.steps < 1:
        parser.error("episodes ve steps pozitif olmalı")
    if args.root.exists():
        parser.error("Çıktı klasörü zaten var. Yeni --root seç; mevcut verinin üzerine yazılmaz.")
    prepare_paths()
    from strands_robots import Robot
    sim = Robot("so101", mode="sim", mesh=False)
    recording = False
    try:
        checked(sim.add_camera(name="front", position=[0.6, -0.6, 0.5], target=[0, 0, 0.15],
                               width=256, height=256), "kamera")
        checked(sim.render(camera_name="front"), "kayıt öncesi kamera testi")
        checked(sim.start_recording(repo_id="local/sim-smoke", root=str(args.root.resolve()),
                                   task="Move the arm for an interface test", fps=30,
                                   cameras=["front"], push_to_hub=False), "kayıt başlat")
        recording = True
        for episode in range(args.episodes):
            checked(sim.reset(), "reset")
            checked(sim.run_policy(robot_name="so101", policy_provider="mock", n_steps=args.steps,
                                   control_frequency=30, seed=episode), f"episode {episode}")
            checked(sim.save_episode(), "episode kaydet")
        checked(sim.stop_recording(), "kayıt bitir")
        recording = False
        checked(sim.verify_dataset_episodes(expected=args.episodes), "episode doğrula")
        (args.root / "ATOLYE_README.json").write_text(json.dumps({
            "purpose": "pipeline-smoke-only", "expert_demonstrations": False,
            "task_success_measured": False, "expected_episodes": args.episodes,
            "expected_frames_per_episode": args.steps,
        }, indent=2))
        print(f"{args.episodes} episode kaydedildi: {args.root}. Bu veri kavrama eğitimi için uzman veri değildir.")
    finally:
        try:
            if recording:
                sim.stop_recording()
        finally:
            sim.cleanup()


if __name__ == "__main__":
    main()
