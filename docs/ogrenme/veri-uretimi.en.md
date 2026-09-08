# How do I produce training data?

Training data is more than a collection of videos. It must show which action belongs to which observation, with defined timing and task. Start by identifying the teacher and what its behavior can actually teach.

The numeric converter's one-action feature is stored as a Parquet scalar in this LeRobot version. The standard reader also returns a scalar tensor; a custom numeric consumer can explicitly use `reshape(1)` when it needs a vector. This storage case does not make a scalar valid for a declared six-action feature.

## Three sources

| Route | Expert | Records | First purpose |
|---|---|---|---|
| Mathematical examples | Known kinematics | Position/angle pairs | Understand a learning calculation |
| Simulation demonstrations | Rules, controller or human | State, action, optionally images | Learn physics and recording |
| Physical demonstrations | Human and leader arm | Cameras, follower state, sent actions | Teach your actual workspace task |

A mock/random policy tests an interface. Recording random movements that never grasp an object does not create a grasping expert. Identify the source in every dataset card.

## 1. Choose the smallest meaningful task

Start with “reach a target hinge angle.” Observation is `[current angle, target angle]`, action is a motor target, and success is final error below 0.04 rad. The [first learning script](ilk-ogrenme.md) generates this inside physics.

For visual pick-and-place, observations include cameras, joint state and task text. Labels can be future motor targets. Success means actually lifting and placing the object. The data contract expands with the task.

## 2. Design one record

```text
episode=12, frame=40, time=0.80 s
observation.state = measured joint positions
observation.images.front = image available at decision time
task = "Pick up the red cube and place it in the tray"
action = target actually sent for that observation
```

Silently pairing a future state with an earlier image introduces a time-alignment error. If a human request differs from the limited command sent to the follower, document which one is recorded. See [data engineering](veri-muhendisligi.md).

## 3. Generate numeric demonstrations in simulation

```bash
.venv-ml/bin/python examples/15_first_learning.py --output outputs/my-first-learning
```

The script creates `demonstrations.csv`: 40 episodes × 100 frames = 4,000 records. The teacher moves toward the goal with small target increments. Goal is included in the observation, so the same current position can request different directions. Episodes are split into train/validation/test, a small model is trained, and fresh physics rollouts evaluate it.

This CSV has no images. It is a complete small numeric learning example, not an image-language-action dataset ready for SmolVLA.

## 4. Convert the CSV into LeRobot format

```bash
.venv-ml/bin/python examples/16_create_lerobot_dataset.py \
  outputs/my-first-learning/demonstrations.csv --root data/my-teaching-hinge
.venv-ml/bin/python examples/04_inspect_dataset.py data/my-teaching-hinge --expected-episodes 40
```

The converter uses the real LeRobot writer:

```python
# Flow summary; the complete runnable converter is in examples/.
dataset = LeRobotDataset.create(repo_id=repo_id, root=root, fps=50,
                               robot_type="teaching_hinge", features=features)
dataset.add_frame(frame)
dataset.save_episode()
dataset.finalize()
```

`features` defines names, dtypes and shapes. Use the writer's timestamp/index contract rather than fabricating fields. Finalization completes pending files and metadata. [LeRobot recording/format API](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

The output is a real LeRobot dataset with robot type `teaching_hinge`, state dimension 2, action dimension 1 and zero cameras. The SO-101-specific `05_prepare_training.py` correctly rejects it. Padding an unrelated robot's action vector to six values does not create compatible SmolVLA data.

## 5. Record images from the SO-101 simulation

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/my-so101-smoke
.venv-ml/bin/python examples/04_inspect_dataset.py data/my-so101-smoke --expected-episodes 3
.venv-ml/bin/python examples/08_read_dataset.py --root data/my-so101-smoke --repo-id local/sim-smoke
```

This exercises image/action recording with the actual SO-101 asset, using a mock policy. To produce grasping demonstrations, implement successful approach/close/lift/release stages from the [controller design](../simulasyon/denetleyici.md), or add human control in simulation. Measure object behavior before labeling success.

## 6. Collect physical demonstrations when the robot arrives

Complete [first power-on](../donanim/ilk-acilis.md) and [teleoperation](../donanim/teleop.md), then record [five pilot episodes](../donanim/veri.md). Review each video. Check visibility, stable cameras, action units, the task ending and gripper behavior before scaling up.

For example, collect from five starting regions using the same object. Change position first; vary lighting or object orientation in another experiment version. More frames do not necessarily mean more distinct situations.

## 7. Store versions and provenance

Keep raw recordings, curated data and split episode lists identifiable. Do not trim your only raw copy. A card such as `ATOLYE_CARD.json` should record units, source script, splits and success definition.

Adding a camera or changing action units calls for a new dataset version. Silently merging incompatible scales can teach conflicting targets. A Hub-ready package must preserve relationships among `meta`, `data` and any `videos`. See [Hub download/sharing](huggingface.md).

**Completion:** explain when and from which teacher a record came, preserve episode boundaries, and validate numerical records separately from videos.
