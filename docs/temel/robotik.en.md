# Coordinates and control

Separate three questions: what pose do I want, which joint configuration achieves it, and how should motors approach it? They belong to task definition, kinematics and control.

## Joints and the tip

We can write `q=[q1,q2,q3,q4,q5,gripper]`, but the six numbers need not share units. Rotary joints might use radians, degrees or normalized values; the gripper can use another range.

Forward kinematics computes tip pose from joints. Inverse kinematics finds joints for a requested tip pose. IK can have several solutions or none; limits, approach and obstacles constrain selection.

```text
x = L1*cos(q1) + L2*cos(q1 + q2)
y = L1*sin(q1) + L2*sin(q1 + q2)
```

This two-link teaching equation uses q2 relative to link one, so the second world angle is q1+q2. Explore it in the [browser lab](laboratuvar.md). It is not the complete SO-101 model. The [worked IK chapter](kinematik-ik.md) develops it further.

## Reference frames

Coordinates such as `(0.2,0.1,0.05)` require a named frame: world/table, robot base, gripper or camera. Pixels are not meters. Recovering a world point from an image needs calibration plus depth or assumptions such as a known plane.

`T_world_camera` names a transform taking camera-frame points into world coordinates. Using its inverse in the wrong place can resemble a sign error. Document units, axes and rotation conventions alongside the matrix.

## Measurement versus command

```text
observation.state[t]   = measured joint positions now
action[t]              = target sent from that observation
observation.state[t+1] = state after physics/control evolves
```

Targets do not happen instantly: load, motor response and timing intervene. Recording state in place of the sent action can lose the teacher command and change the learning problem.

## Units and representations

| Representation | Example | Common mistake |
|---|---|---|
| Meters | 0.10 = 10 cm | Sending 10 for 10 cm |
| Radians | π/2 ≈ 1.571 = 90° | Sending 90 radians |
| Normalized target | Calibration-dependent range | Assuming the same angle on every robot |
| Quaternion | MuJoCo commonly uses w,x,y,z | Copying x,y,z,w without reordering |
| RGB | R,G,B channels | Leaving OpenCV BGR unchanged |

MJCF input angles depend on compiler settings; compiled rotary-joint runtime values are radians. Box `geom size` uses half-sizes. Verify API contracts in the [XML reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html).

## Three clocks

At 0.002 s, physics runs 500 steps per simulated second. Control at 30 Hz supplies a target roughly every 0.0333 s. Camera FPS can differ. These are separate counters.

`0.0333/0.002≈16.67` is not an integer, so inspect substep scheduling. `step(30)` does not automatically mean one second. Dataset FPS must describe recorded control samples appropriately.

## Simple feedback

A position controller uses target minus measurement as an error. Proportional control scales correction with that error; damping/derivative behavior can reduce oscillation. Larger gains are not always better and can increase oscillation or contact forces. Start with the [hinge experiment](../simulasyon/mujoco.md), inspect a time history, then move to [measured SO-101 tracking](../simulasyon/denetleyici.md).
