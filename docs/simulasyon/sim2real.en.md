# From simulation to hardware

Visual resemblance does not solve policy transfer. Check four contracts: **input, action, timing and physics**.

## 1. Inputs

Match camera names, views, resolution, color order and preprocessing. Renaming a key does not make a side view equivalent to an overhead view. Occlusion on the real arm can change the observation distribution substantially.

Joint state is also input: every element needs the correct name, order and unit. Simulated radians and calibrated normalized hardware values are different. Matching vector length does not prove compatibility.

## 2. Actions

Complete this card before applying simulated actions to hardware:

```text
action_order: [joint names in order]
arm_units: radians / degrees / normalized
gripper_units: specified separately
command_semantics: absolute position / delta position / velocity / torque
normalization: dataset statistics and inverse transform
control_hz: ...
joint_limits_and_step_limits: ...
```

Strands' embodiment/processor layer supports mappings, but inspect the actual one selected for your robot and policy using sample states/actions. Renaming a field does not convert radians to degrees. [Local LeRobot policy](https://github.com/strands-labs/robots/blob/main/docs/policies/lerobot-local.md)

## 3. Timing

Replaying the same number of actions at 10 Hz instead of their recorded 30 Hz changes duration. Camera age, USB readings, inference and chunk execution all affect behavior. Measure requested and achieved loop periods.

Begin transfer evaluation with short runs in a restricted task region. Inspect action ranges and latency before longer rollouts. Perfect simulated success cannot verify real calibration.

## 4. Physics

Backlash, cables, friction, motor response and printed-part compliance differ from idealized models. Object mass, jaw surface and contact points affect grasping. Extremely broad randomization without measurements is not automatically realistic.

Domain randomization varies conditions over controlled ranges to reduce dependence on one setting. Relate ranges to observed variation in your workspace. Vary visual and physical factors in separate experiments so their effects can be measured.

## A practical route

1. Make the simulation interface and recording pipeline work.
2. On delivery, verify joint directions and camera contracts.
3. Record five physical pilot episodes and test the small training pipeline.
4. Increase the amount/diversity of task-relevant real demonstrations.
5. If using simulation pretraining, compare its real-data fine-tuning against a real-only baseline.

Simulation plus real data is not guaranteed to outperform real data alone. Compare real-only, sim-to-real fine-tuning and mixed-data runs on the same test conditions, documenting different data volumes and training budgets.

## Inspect failures

| Observation | First things to inspect |
|---|---|
| Wrong direction | Names/order, units, sign, calibration |
| Right direction, misses target | Camera pose, base frame, latency |
| Reaches object, cannot hold | Gripper direction, width, surface, contact |
| Drops while lifting | Grasp geometry, speed, mass, gripper limits |
| Starts well, drifts later | Open-loop horizon, unseen states, recovery data |

If the cause is unknown, do not make “double the training steps” your first action. More optimizer updates cannot repair a wrongly mapped camera.
