"""Gerçek SO-101 simülasyon varlığı: durum, kısa mock rollout, isteğe bağlı PNG."""
import argparse
import json
from common import ROOT, checked, payload, prepare_paths, save_render


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--viewer", action="store_true", help="Masaüstü MuJoCo penceresi; macOS'ta mjpython kullan")
    parser.add_argument("--steps", type=int, default=30)
    args = parser.parse_args()
    if not 1 <= args.steps <= 3000:
        parser.error("steps 1–3000 olmalı")
    prepare_paths()
    from strands_robots import Robot
    sim = Robot("so101", mode="sim", mesh=False)
    try:
        checked(sim.add_object(name="cube", shape="box", size=[0.02, 0.02, 0.02],
                               position=[0.22, 0.08, 0.025], color=[1, 0.4, 0.2, 1], mass=0.03), "küp")
        checked(sim.add_camera(name="front", position=[0.65, -0.65, 0.50],
                               target=[0.05, 0, 0.18], width=960, height=640), "kamera")
        state = checked(sim.get_robot_state("so101"), "durum")
        print(json.dumps(state, ensure_ascii=False, indent=2, default=str))
        if args.render:
            path = save_render(sim.render(camera_name="front"), ROOT / "outputs/so101_before.png")
            print(f"Başlangıç görüntüsü: {path}")
        if args.viewer:
            checked(sim.open_viewer(), "MuJoCo penceresi")
        result = checked(sim.run_policy(robot_name="so101", policy_provider="mock",
                         instruction="Interface smoke test; no grasping objective",
                         n_steps=args.steps, control_frequency=30, seed=7), "mock rollout")
        print(json.dumps(payload(result), ensure_ascii=False, indent=2, default=str))
        if args.render:
            path = save_render(sim.render(camera_name="front"), ROOT / "outputs/so101_after.png")
            print(f"Son görüntü: {path}")
        print("Başarılı API testi. Mock hareket, küp kavrama veya eğitilmiş politika başarısı değildir.")
    finally:
        sim.cleanup()


if __name__ == "__main__":
    main()
