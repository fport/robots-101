"""SO-101 siminde ölçülen durumla üç eklem-uzayı hedefini takip et; CSV/JSON üret."""
import argparse
import csv
import json
import math
from pathlib import Path
import time

from common import ROOT, checked, payload, prepare_paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/waypoints")
    parser.add_argument("--viewer", action="store_true")
    parser.add_argument("--timeout", type=float, default=8.0, help="Hedef başına sim saniyesi")
    args = parser.parse_args()
    if not math.isfinite(args.timeout) or not .1 <= args.timeout <= 60:
        parser.error("timeout 0.1–60 saniye olmalı")
    if args.output.exists():
        parser.error("Çıktı mevcut; yeni bir --output seç")
    prepare_paths()
    from strands_robots import Robot

    sim = Robot("so101", mode="sim", mesh=False)
    rows, outcomes = [], []
    try:
        keys = sim.robot_action_keys("so101")
        # This exercise is intentionally tied to the inspected SO101 asset.
        if keys != [str(i) for i in range(1, 7)]:
            raise RuntimeError(f"Model eşlemesi değişti; beklenen 1..6, gelen {keys}")
        dt = sim.physics_timestep()
        control_dt = .02
        substeps = round(control_dt / dt)
        if substeps < 1 or not math.isclose(substeps * dt, control_dt, abs_tol=1e-9):
            raise RuntimeError(f"50 Hz kontrol, fizik timestep={dt} ile tam bölünmüyor")

        def read():
            state = payload(checked(sim.get_robot_state("so101"), "state"))["state"]
            q = [state[k]["position"] for k in keys]
            if not all(math.isfinite(v) for v in q):
                raise RuntimeError("Sonlu olmayan eklem durumu")
            return q

        if args.viewer:
            checked(sim.open_viewer(), "viewer")
        targets = [[.25, 0, 0, 0, 0, 0], [-.25, 0, 0, 0, 0, 0], [0.] * 6]
        tolerance, dwell_steps, command_rate = .04, 10, .5
        command = read()
        step = 0
        args.output.mkdir(parents=True, exist_ok=False)
        for waypoint, target in enumerate(targets):
            dwell = 0
            start_step = step
            for _ in range(math.ceil(args.timeout / control_dt)):
                started = time.monotonic()
                before = read()
                # Slew limit the commanded reference, not the measured joint speed.
                command = [c + max(-command_rate * control_dt,
                                  min(command_rate * control_dt, g - c))
                           for c, g in zip(command, target)]
                checked(sim.send_action(dict(zip(keys, command)), robot_name="so101",
                                        n_substeps=substeps), "send_action")
                after = read()
                error = max(abs(q - g) for q, g in zip(after, target))
                dwell = dwell + 1 if error <= tolerance else 0
                row = {"step": step, "time_before_s": step * control_dt,
                       "time_after_s": (step + 1) * control_dt,
                       "waypoint": waypoint, "max_error_rad": error, "dwell_steps": dwell}
                for i, key in enumerate(keys):
                    row.update({f"q_before_{key}": before[i], f"command_{key}": command[i],
                                f"q_after_{key}": after[i], f"goal_{key}": target[i]})
                rows.append(row)
                step += 1
                if args.viewer:
                    time.sleep(max(0, control_dt - (time.monotonic() - started)))
                if dwell >= dwell_steps:
                    break
            outcomes.append({"waypoint": waypoint, "goal_rad": target,
                             "success": dwell >= dwell_steps,
                             "duration_sim_s": (step - start_step) * control_dt,
                             "final_max_error_rad": error})
            if dwell < dwell_steps:
                break
        with (args.output / "trajectory.csv").open("x", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        report = {"task": "SO101 joint-space pan waypoints; no grasp task",
                  "keys": keys, "units": "radians in this MuJoCo asset",
                  "control_hz": 50, "physics_dt": dt, "substeps": substeps,
                  "command_slew_rad_s": command_rate, "tolerance_rad": tolerance,
                  "required_dwell_steps": dwell_steps, "steps": step,
                  "sim_duration_s": step * control_dt, "outcomes": outcomes,
                  "success": len(outcomes) == len(targets) and all(x["success"] for x in outcomes)}
        (args.output / "metrics.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
        if not report["success"]:
            raise SystemExit(1)
    finally:
        sim.cleanup()


if __name__ == "__main__":
    main()
