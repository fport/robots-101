# Evaluation and policy execution

Define success before running a policy. For example: within 25 seconds, lift the object, place it inside the tray, release it, retreat the gripper and leave the object there for two seconds. A hand above the tray or a low training loss does not establish this outcome.

## Check the deployment contract

Match camera feature names, image processing, action order and units, normalization statistics, robot IDs and calibration. These hardware recipes use `use_degrees=false`, unlike radians in the simulator. Six numbers on both sides do not guarantee compatibility.

The physical commands below were not tested with an attached SO-101. Complete [hardware setup](../donanim/ilk-acilis.md) and [teleoperation](../donanim/teleop.md) first. Begin with a clear workspace and a short supervised run.

## A five-second hardware rollout

This command **moves the physical robot**. Use the actual checkpoint produced by your run and the port/camera variables from the hardware chapters:

```bash
source .venv-ml/bin/activate
export POLICY_PATH='outputs/train/smolvla-pick-v1/checkpoints/last/pretrained_model'
lerobot-rollout \
  --strategy.type=base \
  --policy.path="$POLICY_PATH" \
  --device=mps \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false \
  --robot.max_relative_target=2 \
  --robot.cameras="$CAMERAS" \
  --task='Pick up the red cube and place it in the tray.' \
  --fps=30 --duration=5
```

Choose `cpu`, `mps` or `cuda` for the actual environment; this page does not claim that MPS achieves 30 Hz. `max_relative_target=2` is a relative target limit in normalized units, not a certified speed limit. Measure image age, model latency and observed control timing.

## Strands local policy template

Once a compatible model and simulation observation/action mapping exist, the API surface is:

```python
# Untested integration template: sim is an existing simulation object.
result = sim.run_policy(
    robot_name="so101",
    policy_provider="lerobot_local",
    policy_config={
        "pretrained_name_or_path": "/ABSOLUTE/PATH/TO/pretrained_model",
        "device": "cpu",
        "strict_keys": True,
    },
    instruction="Pick up the red cube and place it in the tray.",
    control_frequency=30,
    n_steps=30,
)
```

This template was inspected against the Strands source; a full SmolVLA rollout was not executed. Preserve strict feature checking and solve mismatches. A hardware-trained policy needs matching camera, joint and gripper semantics before simulation use. [Strands Robots](https://github.com/strands-labs/robots)

The `STRANDS_TRUST_REMOTE_CODE` gate relates to loading trusted model code. Do not treat it as a camera-key fix or broadly disable validation. Review the model source and trust configuration before enabling remote-code execution for a specific integration.

## Record every attempt

Use `templates/evaluation.csv`. These rows illustrate the format; they are not measured robot results:

```csv
episode_id,condition,success,failure_reason,checkpoint,notes
1,center,1,,checkpoint-a,object stayed in tray
2,left,0,grasp_miss,checkpoint-a,fingers closed beside object
3,right,0,drop,checkpoint-a,object dropped during transport
```

```bash
.venv/bin/python examples/06_evaluate_results.py templates/evaluation.csv
```

The script reports counts, success rate, a Wilson 95% interval and failure groups. It rejects empty/duplicate attempts, invalid success labels and missing failure reasons. Use your own observations in a separate file. For meaningful comparisons, preserve checkpoint identity and report conditions separately rather than hiding difficult regions in one pooled rate.

## Read failures by stage

Separate approach, alignment, closure, lift, transport and release. A good approach with poor closure suggests a different next experiment than successful lifting followed by dropping. First check the input/output contract, then timing, coverage and training, using the [experiment guide](egitim-deneyleri.md). Keep failed videos and report small-sample uncertainty; do not select only attractive successful clips.
