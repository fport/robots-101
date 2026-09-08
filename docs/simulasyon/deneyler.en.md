# Ten MuJoCo experiments

Predict, run, then extract a number. `examples/13_mujoco_playground.py` provides five scene behaviors; their parameters support the ten questions below. The model contains a cube and one teaching hinge, not an SO-101.

## 1. Drop and contact

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene drop --output outputs/e01
```

The cube starts at 0.60 m; its center settles near 0.02497 m. Contact count rises from zero. Center height should be near the box half-size. Small penetration can reflect the soft contact solution: examine the difference in millimeters before interpreting it as a large geometry error.

## 2. Disable gravity

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene drop --gravity 0 --output outputs/e02
```

Height stays at 0.60 m and no contacts occur. Only gravity changed. A stationary object can be the correct physical result, rather than a broken simulator.

## 3. Low-friction slide

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 0.1 --output outputs/e03
```

The cube starts near the floor with x velocity 0.8 m/s. The measured displacement was about 0.3256 m. Both floor and cube sliding friction are changed; changing only one can interact differently with contact parameter combination rules.

## 4. High-friction comparison

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 1 --output outputs/e04
```

Displacement was about 0.02976 m. Compare `cube_x_displacement_m` across the two reports. These numbers describe the specified model and start, not a measurement of your actual desk. Keep starting velocity, mass and duration fixed.

## 5. Track a motor target

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --target 0.7 --output outputs/e05
```

The position actuator tracks the reference. After 3 simulated seconds the measured angle is approximately 0.7 rad. `command_rad` is the request; `pan_rad` is the measurement. Its vertical rotation axis makes this different from lifting a shoulder against gravity.

## 6. Gain and damping

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --kp 10 --damping 0.2 --output outputs/e06
```

Proportional gain and damping affect the transient. This command changes both, so it cannot isolate one cause; hold one fixed in your next comparison. Inspect the whole trajectory, not just the final angle.

The script updates both the position actuator's gain and its matching bias term when changing kp. Changing only the gain would not preserve the same controller equations as changing XML kp. [Actuator modeling](https://mujoco.readthedocs.io/en/stable/modeling.html#actuator-shortcuts)

## 7. Apply a short external force

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene push --output outputs/e07
```

For the first 0.20 s a 0.4 N world-x force is applied, then removed. The script clears `xfrc_applied` every step so an old force does not persist accidentally. The local run moved about 0.05828 m. This applies force directly to the body; it does not simulate a physical gripper pushing it.

## 8. Seeded starting conditions

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene random --seed 7 --output outputs/e08a
.venv/bin/python examples/13_mujoco_playground.py --scene random --seed 7 --output outputs/e08b
.venv/bin/python examples/13_mujoco_playground.py --scene random --seed 8 --output outputs/e08c
```

The first two initial positions should match in the same software environment; the third changes. The script varies cube position and color, not every physical property. For domain randomization, document each varied parameter and its distribution.

## 9. RGB and depth

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --render --output outputs/e09
```

`rgb.png` is a 640×480 color image; `depth_m.npy` contains per-pixel metric depth. Change the camera in a copy of the XML and compare visibility. Ideal simulated depth is not data that an ordinary real RGB camera automatically supplies.

Images were produced on this Mac, but the graphics driver reported limited depth accuracy (`ARB_clip_control`). File creation is therefore not presented as a precision depth calibration. [Rendering API](https://mujoco.readthedocs.io/en/stable/python.html)

## 10. Reset and repeat

Each run finishes with `mj_resetData`, restoration of saved initial positions/velocities and `mj_forward`. Expect `reset_time_s=0` and `reset_qpos_max_error=0`. State reset does not automatically revert model properties such as changed friction or color.

Distinguish sampling a new start with a new seed from restoring a saved start. Both are useful, but answer different experimental questions.

## Connect the experiments to SO-101

Proceed to [tracking with the actual SO-101 asset](denetleyici.md): six action keys, measured errors and stage transitions. Then connect [recording](veri.md) and [learning](../ogrenme/ilk-ogrenme.md).

**Completion:** preserve at least three CSV/JSON runs, compare a number and explain the changed cause. Opening a window alone does not complete these experiments.
