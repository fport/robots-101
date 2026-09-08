# Build a simulation from scratch

Start with [your first robotics introduction](../basla/sifirdan.md). By the end of this chapter, you should understand both how to launch a simulation and how to design an experiment with it.

## Understand what you are building

A **scene** contains a floor, objects, lights, cameras and optionally a robot. The **model** defines geometry, mass, joints and contact properties. The **state** contains current positions and velocities. A **physics step** advances time. **Rendering** generates an image from a camera.

Keep the sequence clear: **define the scene → choose a start → apply a force or command → advance time → measure**. A learning model can later become the decision maker inside this loop. Installing MuJoCo does not automatically teach a task.

## 1. Open the project directory

On this machine:

```bash
cd /Users/furkanportakal/www/robots
pwd
```

Use your own checkout path elsewhere. `models/`, `examples/` and `requirements-sim.txt` belong under the same root. If `.venv` is already prepared, skip to step 3; do not delete it just to repeat an experiment.

## 2. Prepare Python and MuJoCo

Check `uv --version`. If it is missing, follow the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-docs.txt -r requirements-sim.txt
.venv/bin/python examples/00_doctor.py
```

The virtual environment isolates project dependencies. No Hugging Face account or paid GPU is needed for these initial physics experiments. Package installation needs internet. Commands target macOS/Linux; Windows/WSL and physical USB access have not been validated here.

## 3. Run physics without a window

```bash
.venv/bin/python examples/13_mujoco_playground.py \
  --scene drop --output outputs/my-first-drop
```

The cube's center starts at 0.60 m and settles near 0.025 m. Its side is 5 cm, so the center should not end at z=0. The terminal prints a report; `metrics.json` and `trajectory.csv` are saved under your output directory.

The CSV records time, cube coordinates, joint angle and contact count at each physics step. Contact count is not a successful-grasp label. Existing output directories are refused: choose another name to preserve your previous experiment.

## 4. Read the scene file

`models/playground.xml` contains the complete runnable scene. Its structure is:

```xml
<mujoco>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <worldbody>
    <!-- floor, camera, free cube and a one-joint teaching arm -->
  </worldbody>
  <actuator>
    <!-- a position actuator that tracks the joint target -->
  </actuator>
</mujoco>
```

This abbreviated block explains the structure; use the complete project file to run it. MuJoCo's native XML model format is called MJCF. `body` defines a rigid body, `geom` its geometry/contact shape, and `joint` its movement freedoms. The cube's `freejoint` lets it move in space; without a joint it would be fixed to its parent body. [MuJoCo modeling](https://mujoco.readthedocs.io/en/stable/modeling.html)

For a box, `size="0.025 0.025 0.025"` contains half-sizes, producing 0.05 m edges. `mass="0.05"` is 50 grams. Always write down units when changing values.

## 5. Understand the Python loop

```python
model = mujoco.MjModel.from_xml_path("models/playground.xml")
data = mujoco.MjData(model)
for _ in range(1500):
    mujoco.mj_step(model, data)
print(data.time)
```

1500 steps at 0.002 seconds produce 3 simulated seconds. This need not take 3 wall-clock seconds. `model` is the world definition; `data` is changing state. `mj_forward` refreshes derived calculations after changing state; it does not itself advance time. [Python API](https://mujoco.readthedocs.io/en/stable/python.html)

The teaching scene has `nq=8`, `nv=7`, `nu=1`. The free cube's position/quaternion and velocity also occupy the state vectors. Eight position values do not mean eight motors. Name-based access such as `model.joint("pan")` identifies the joint you intend to use.

## 6. Open a view

On macOS:

```bash
.venv/bin/mjpython examples/13_mujoco_playground.py \
  --scene drop --viewer --output outputs/drop-window
```

On a Linux desktop, use `.venv/bin/python` with the same arguments. The viewer adds wall-clock pacing. To save RGB and depth:

```bash
.venv/bin/python examples/13_mujoco_playground.py \
  --scene servo --render --output outputs/servo-camera
```

This produces `rgb.png` and `depth_m.npy`. Rendering needs a graphics context. If graphics fail, first verify windowless physics. A macOS sandbox can block graphics; setting `MUJOCO_GL=egl` is not a general Mac fix. Background/far-plane depth values must not all be interpreted as object distance.

## 7. Change one cause

```bash
.venv/bin/python examples/13_mujoco_playground.py \
  --scene drop --gravity 0 --output outputs/drop-no-gravity
```

With zero initial velocity, the cube stays at 0.60 m. Predict this before running. Do not conclude that objects cannot move without gravity: an initial velocity or external force can still produce motion.

## What can you do with this environment?

| Purpose | Experiment | Measurement |
|---|---|---|
| Understand physics | Drop, slide, push | Position, velocity, contact |
| Understand control | Change target and damping | Tracking error, oscillation |
| Place cameras | Change viewpoint/resolution | Visibility, RGB/depth |
| Repeat conditions | Reset and reuse a seed | Initial state, outcome difference |
| Generate data | Run an expert rule and record | Aligned observations/actions, episodes |
| Try learning | Train a small policy and rerun physics | Held-out task performance |
| Move to SO-101 | Load the asset through Strands | Six action keys, camera, tracking |

MuJoCo is not by itself an object detector, task planner, demonstration expert or trainer. You or another library add those components. Real-world fidelity also depends on the model you define.

## Design your own experiment

Before writing code, specify six things: **task, starting distribution, observation, action, success, timeout**. Example: push a cube starting at x=0.12 m, observe x, apply a force for 0.2 s, require at least 4 cm displacement, stop after 3 s. This separates an attractive image from a completed task.

Continue with [ten MuJoCo experiments](deneyler.md), [Strands and SO-101](strands.md), or [your first learning loop](../ogrenme/ilk-ogrenme.md).
