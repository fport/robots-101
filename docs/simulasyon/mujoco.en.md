# Understanding MuJoCo

MuJoCo is a physics engine for articulated bodies and contact; its name comes from Multi-Joint dynamics with Contact. This workshop uses CPU physics, while rendering requires a graphics context. [Overview](https://mujoco.readthedocs.io/en/stable/overview.html)

For a guided first setup, read [simulation from scratch](sifirdan.md); for more uses, try [ten experiments](deneyler.md).

## Four components

The **model** defines geometry, joints, masses, limits and actuators. **State** contains current positions/velocities. **Control** supplies actuator requests. **Stepping** advances physics.

```python
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)
data.ctrl[0] = 0.7
mujoco.mj_step(model, data)
```

The meaning of `data.ctrl` depends on the XML actuator. A position actuator can take an angle target, while a motor actuator has a torque-related control mapping. The same number is not the same physical request in both.

## Read the teaching MJCF

`examples/01_mujoco_basics.py` contains a single rotary joint:

| XML element | Meaning |
|---|---|
| `compiler angle="radian"` | XML joint angles use radians |
| `option timestep="0.002"` | Two milliseconds per physics step |
| `body` | Rigid body |
| `joint type="hinge" axis="0 0 1"` | Rotation about z |
| `geom type="capsule"` | Link geometry/contact shape |
| `site name="tip"` | Tip marker |
| `position ... kp="25"` | Position-tracking actuator |

`geom` and `joint` describe different things. A realistic-looking mesh does not establish accurate mass, friction or contact behavior. [Modeling guide](https://mujoco.readthedocs.io/en/stable/modeling.html)

## Run and vary one parameter

```bash
.venv/bin/python examples/01_mujoco_basics.py --target 0.7
.venv/bin/python examples/01_mujoco_basics.py --target -0.4
```

This early exercise overwrites the same CSV; save a copy before comparing runs. Plot time, measured angle and target in a spreadsheet. Change target sign, then compare kp=25 against kp=10, then change damping independently. Examine the full transient rather than one last frame.

The joint axis is vertical, so gravity does not load it like a lifting shoulder. A gravity-loaded arm experiment needs another axis/geometry. Keep a note of edits so you can restore the model.

## Stepping, forward calculation and rendering

`mj_step` advances time. `mj_forward` updates derived calculations from the current state without advancing time. Rendering creates an image; it does not train a policy.

Do not equate qpos length with motor count: free objects contribute position/quaternion coordinates. Use named robot joints rather than treating the entire scene state as six arm angles.

## Windows and headless execution

Use `mjpython` for the macOS passive viewer. Linux can use desktop OpenGL/GLFW or an appropriate EGL server setup. `MUJOCO_GL=egl` neither installs a driver nor serves as a universal Mac fix. When rendering fails, test physics without images to isolate the layer. [Python viewer/rendering](https://mujoco.readthedocs.io/en/stable/python.html)

Next, [load SO-101 with Strands](strands.md) instead of writing its full model yourself.
