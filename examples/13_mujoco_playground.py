"""Five small MuJoCo experiments: drop, slide, servo, push and seeded variation."""
import argparse
import csv
import json
from pathlib import Path
import time

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def make_scene(scene="drop", gravity=-9.81, friction=.6, kp=25., damping=1., seed=42):
    model = mujoco.MjModel.from_xml_path(str(ROOT / "models/playground.xml"))
    model.opt.gravity[2] = gravity
    model.geom_friction[:, 0] = friction
    pan = model.joint("pan").id
    model.dof_damping[model.jnt_dofadr[pan]] = damping
    act = model.actuator("pan_target").id
    # A position actuator has gain=kp and bias=-kp*q, so update BOTH terms.
    model.actuator_gainprm[act, 0] = kp
    model.actuator_biasprm[act, 1] = -kp
    data = mujoco.MjData(model)
    cube_q = model.jnt_qposadr[model.joint("cube_free").id]
    cube_v = model.jnt_dofadr[model.joint("cube_free").id]
    if scene in {"slide", "push"}:
        data.qpos[cube_q + 2] = .026
    if scene == "slide":
        data.qvel[cube_v] = .8
    if scene == "random":
        rng = np.random.default_rng(seed)
        data.qpos[cube_q:cube_q + 3] = [rng.uniform(-.1, .2), rng.uniform(-.15, .15), rng.uniform(.25, .7)]
        model.geom_rgba[model.geom("cube_geom").id, :3] = rng.uniform(.2, 1, 3)
    mujoco.mj_forward(model, data)
    return model, data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", choices=["drop", "slide", "servo", "push", "random"], default="drop")
    parser.add_argument("--seconds", type=float, default=3)
    parser.add_argument("--gravity", type=float, default=-9.81)
    parser.add_argument("--friction", type=float, default=.6)
    parser.add_argument("--kp", type=float, default=25.)
    parser.add_argument("--damping", type=float, default=1.)
    parser.add_argument("--target", type=float, default=.7)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--render", action="store_true", help="Save RGB PNG and metric depth NPY after the run")
    parser.add_argument("--viewer", action="store_true", help="macOS: use mjpython")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/playground")
    args = parser.parse_args()
    if not all(np.isfinite(x) for x in [args.seconds, args.gravity, args.friction, args.kp, args.damping, args.target]):
        parser.error("All numeric settings must be finite")
    if not (.05 <= args.seconds <= 60 and -20 <= args.gravity <= 0 and 0 <= args.friction <= 2
            and .1 <= args.kp <= 100 and 0 <= args.damping <= 10 and -1.5 <= args.target <= 1.5):
        parser.error("Settings outside the documented teaching range")
    if args.output.exists():
        parser.error("Output exists; choose a new --output")
    model, data = make_scene(args.scene, args.gravity, args.friction, args.kp, args.damping, args.seed)
    initial_qpos, initial_qvel = data.qpos.copy(), data.qvel.copy()
    cube = model.body("cube").id
    pan_q = model.jnt_qposadr[model.joint("pan").id]
    start_x = float(data.xpos[cube, 0])
    rows = []
    viewer = None
    try:
        if args.viewer:
            from mujoco import viewer as mj_viewer
            viewer = mj_viewer.launch_passive(model, data)
        for _ in range(round(args.seconds / model.opt.timestep)):
            tick = time.monotonic()
            if viewer is not None and not viewer.is_running():
                break
            data.ctrl[model.actuator("pan_target").id] = args.target if args.scene == "servo" else 0
            data.xfrc_applied[:] = 0
            if args.scene == "push" and data.time < .20:
                data.xfrc_applied[cube, 0] = .4  # world-frame force in newtons
            mujoco.mj_step(model, data)
            mujoco.mj_forward(model, data)  # refresh derived positions for the new qpos
            if not np.isfinite(data.qpos).all():
                raise RuntimeError("Non-finite state")
            rows.append({"time_s": float(data.time), "cube_x_m": float(data.xpos[cube, 0]),
                         "cube_y_m": float(data.xpos[cube, 1]), "cube_z_m": float(data.xpos[cube, 2]),
                         "pan_rad": float(data.qpos[pan_q]), "command_rad": float(data.ctrl[0]),
                         "contacts": int(data.ncon), "force_x_N": float(data.xfrc_applied[cube, 0])})
            if viewer is not None:
                viewer.sync()
                time.sleep(max(0, model.opt.timestep - (time.monotonic() - tick)))
        if not rows:
            raise RuntimeError("No physics steps executed")
        args.output.mkdir(parents=True, exist_ok=False)
        with (args.output / "trajectory.csv").open("x", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        report = {"scene": args.scene, "seed": args.seed, "steps": len(rows),
                  "settings": {k: getattr(args, k) for k in ["gravity", "friction", "kp", "damping", "target"]},
                  "nq": model.nq, "nv": model.nv, "nu": model.nu,
                  "initial_qpos": initial_qpos.tolist(), "final": rows[-1],
                  "cube_x_displacement_m": rows[-1]["cube_x_m"] - start_x,
                  "max_contact_count": max(row["contacts"] for row in rows),
                  "scope": "Teaching cube and one hinge; not SO101 or a grasping policy"}
        if args.render:
            from PIL import Image
            with mujoco.Renderer(model, height=480, width=640) as renderer:
                renderer.update_scene(data, camera="overview")
                Image.fromarray(renderer.render()).save(args.output / "rgb.png")
                renderer.enable_depth_rendering()
                renderer.update_scene(data, camera="overview")
                depth = renderer.render().copy()
                np.save(args.output / "depth_m.npy", depth)
                report["depth_range_m"] = [float(depth.min()), float(depth.max())]
        mujoco.mj_resetData(model, data)
        data.qpos[:] = initial_qpos
        data.qvel[:] = initial_qvel
        mujoco.mj_forward(model, data)
        report["reset_time_s"] = float(data.time)
        report["reset_qpos_max_error"] = float(np.max(np.abs(data.qpos - initial_qpos)))
        (args.output / "metrics.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
    finally:
        if viewer is not None:
            viewer.close()


if __name__ == "__main__":
    main()
