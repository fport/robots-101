# Capstone: cube to tray

Produce a successful task video and an interpretable experiment report, with data, training and evaluation artifacts linked together. The report should let you reconstruct the experiment on another day.

## Define the project

Pick up one red cube from a fixed workspace and place it in a particular tray. Keep table/cameras fixed and vary starts across five small regions. Success means the cube remains inside, the gripper retreats and the time limit is respected. Example failure labels: `approach_miss`, `grasp_miss`, `drop`, `place_miss`, `timeout`, `system_error`.

Distinguish system faults from policy behavior in the report. Define how a USB disconnect is counted before testing; do not silently remove it afterward.

## A · Before the robot arrives

Complete setup, MuJoCo tracking and SO-101 rendering. Record three simulation episodes, inspect Parquet and decode video. Use the browser planner to estimate recording/reset time. Also complete the new [physics learning loop](../ogrenme/ilk-ogrenme.md).

**Deliver:** environment report, simulation PNGs, dataset integrity report and a decoded frame. This establishes infrastructure; it does not produce a grasping policy.

## B · Physical pilot

Complete the device card and calibration. Record five demonstrations while checking camera views. Fix task text, reset, visibility and unit problems.

**Deliver:** five readable episodes, camera placement notes/photo, recording command and calibration IDs.

## C · Dataset version 1

Collect balanced successful demonstrations across the starting regions. Label or separate failures. Reserve validation episodes and final test conditions. Do not randomly scatter neighboring frames across splits.

**Deliver:** data root/revision, quality report, split description and task contract.

## D · Two learning experiments

Prepare ACT and SmolVLA on the same data. Run short pipeline checks first. Record settings, wall time, peak memory and checkpoint steps. Equal optimizer update counts can consume different compute for different models.

**Deliver:** loss logs, checkpoints with processors, and complete training commands.

## E · Test

Four repetitions in each of five regions gives an illustrative 20-attempt protocol. Balance model order, preserve reset conditions, save all videos and label every failure.

```text
Model        Success    Main failure    p95 inference    Conditions
ACT-v1       measure    measure         measure          same test
SmolVLA-v1   measure    measure         measure          same test
SmolVLA-v2   measure    measure         measure          same test
```

These are placeholders, not reported results. If you repeatedly tune using these outcomes, the set becomes model-selection data; reserve a new final test.

## F · One targeted improvement

If `grasp_miss` dominates, investigate visibility, position coverage or approach demonstrations. State a hypothesis, change one factor, create data/checkpoint version 2 and compare under the same validation protocol.

```text
outputs/project-report/
  experiment.md
  environment.txt
  data-contract.json
  training-command.sh
  evaluation.csv
  metrics.json
  videos/
```

Start from `templates/experiment.md` and `templates/evaluation.csv`; document the execution order in a README. Describe the conditions actually tested and those still unmeasured.
