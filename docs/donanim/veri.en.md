# Collecting useful demonstrations

Keep the first task narrow: **“Pick up the red cube and place it in the tray.”** Use the same task text for recording and evaluation. This English instruction is a practical starting choice for the model ecosystem; Turkish instruction following requires a separate experiment. Translating this website does not teach a policy another language.

## Record five pilot episodes

The variables come from [teleoperation](teleop.md). This command operates the physical robot:

```bash
source .venv-ml/bin/activate
export DATASET_ID='local/so101-pick-v1'
export TASK='Pick up the red cube and place it in the tray.'

lerobot-record \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false \
  --robot.max_relative_target=2 \
  --robot.cameras="$CAMERAS" \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.use_degrees=false \
  --dataset.repo_id="$DATASET_ID" \
  --dataset.root=data/so101-pick-v1 \
  --dataset.single_task="$TASK" \
  --dataset.fps=30 \
  --dataset.num_episodes=5 \
  --dataset.episode_time_s=25 \
  --dataset.reset_time_s=20 \
  --dataset.push_to_hub=false
```

`local/...` is a local dataset identity here. With upload disabled it does not create a Hub account or repository. Follow the terminal's recording controls to end an episode early, retry it or end the session. A software stop is different from disconnecting physical power. [Official recording guide](https://huggingface.co/docs/lerobot/en/il_robots#record-a-dataset)

## Watch every pilot

1. Are the object, fingers and tray visible at critical moments?
2. Does the episode begin at the actual task start, or contain unnecessary waiting?
3. Are the state/action differences consistent with the movement?
4. Does the same instruction always describe the demonstrated destination?
5. Does the object actually leave the table and then leave the gripper?
6. Does the final image show success, rather than just a gripper above the tray?

Fix camera placement, task definition or operator behavior before enlarging a poor pilot dataset. Extra optimizer steps cannot replace missing demonstrations of successful contact.

## Grow the dataset deliberately

An initial workshop plan is about ten successful demonstrations in each of five starting regions: 50 episodes total. This is an experiment plan, not a universal minimum or success guarantee. Task difficulty, variation and compatibility with pretraining matter.

Vary the object's starting position within a small range while keeping cameras fixed. Introduce lighting variation as a documented change in a later version. Label failures if you retain them; do not silently mix arbitrary failed actions into the first successful-demonstration behavior cloning set.

Before appending recordings, inspect your version's `--resume` behavior: an additional episode count may differ from a desired total count. If the schema, cameras, calibration or units change, create a new version such as `so101-pick-v2`. Keep backups, a file manifest and experiment notes together. Hub upload is optional; choose visibility deliberately when images include people or private surroundings.

## Count decisions, not just pictures

`episodes × seconds × FPS` gives decision rows. For 50 × 20 × 30, that is 30,000 rows. Two cameras give 60,000 images but still 30,000 actions. The [interactive planner](../temel/laboratuvar.md) estimates raw RGB storage; compressed video size depends on encoding and content.

Separate validation by episode so neighboring frames do not leak across the split. For a stronger final test, reserve recording days or starting regions. Repeatedly selecting a model using final test results makes that set part of model selection. Continue with [dataset inspection](../ogrenme/dataset.md), then [training](../ogrenme/smolvla.md).
