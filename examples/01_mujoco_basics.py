"""Yalnız MuJoCo: tek eklemde hedef takip; SO-101 modeli değildir."""
import argparse
import json
import time
from pathlib import Path

import mujoco
import numpy as np

XML = """
<mujoco model="tek_eklem_atolyesi">
  <compiler angle="radian"/>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <worldbody>
    <light pos="0 -1 2"/>
    <geom type="plane" size="1 1 0.1" rgba="0.12 0.16 0.2 1"/>
    <body pos="0 0 0.1">
      <joint name="pan" type="hinge" axis="0 0 1" range="-1.5 1.5" damping="1"/>
      <geom type="capsule" fromto="0 0 0 0.3 0 0" size="0.025" mass="0.3" rgba="0.2 0.85 0.7 1"/>
      <site name="tip" pos="0.3 0 0" size="0.035" rgba="1 0.6 0.2 1"/>
    </body>
  </worldbody>
  <actuator><position name="pan_target" joint="pan" kp="25" ctrlrange="-1.5 1.5"/></actuator>
</mujoco>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--viewer", action="store_true")
    parser.add_argument("--target", type=float, default=0.7, help="radyan; [-1.5, 1.5]")
    args = parser.parse_args()
    if not np.isfinite(args.target) or not -1.5 <= args.target <= 1.5:
        parser.error("target sonlu ve [-1.5, 1.5] arasında olmalı")
    model = mujoco.MjModel.from_xml_string(XML)
    data = mujoco.MjData(model)
    data.ctrl[0] = args.target
    history = []

    def step():
        mujoco.mj_step(model, data)
        history.append([float(data.time), float(data.qpos[0]), float(data.ctrl[0])])

    if args.viewer:
        from mujoco import viewer as mj_viewer
        with mj_viewer.launch_passive(model, data) as viewer:
            for _ in range(1500):
                if not viewer.is_running():
                    break
                start = time.perf_counter()
                step()
                viewer.sync()
                time.sleep(max(0, model.opt.timestep - (time.perf_counter() - start)))
    else:
        for _ in range(1500):
            step()
    error = abs(float(data.qpos[0]) - args.target)
    out = Path(__file__).resolve().parents[1] / "outputs"
    out.mkdir(exist_ok=True)
    np.savetxt(out / "joint_tracking.csv", history, delimiter=",", header="time_s,q_rad,target_rad", comments="")
    print(json.dumps({"simulation_seconds": float(data.time), "target_rad": args.target,
                      "position_rad": float(data.qpos[0]), "error_rad": error}, indent=2))
    if not args.viewer and (not np.isfinite(data.qpos).all() or error > 0.02):
        raise SystemExit("Hedef takip testi başarısız.")


if __name__ == "__main__":
    main()
