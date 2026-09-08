# 22 practical labs

Ask one question per experiment, preserve the output and write a one-sentence finding. Completion criteria measure workshop progress. Start labs 17–19 early if you want more physics practice before robot-specific work.

## Lab 01 · Identify your environment

```bash
.venv/bin/python examples/00_doctor.py
.venv-ml/bin/python examples/00_doctor.py
```

Expect different interpreter paths and LeRobot/PyTorch in the ML environment. Compare with system `python3` and explain missing packages. Finish by recording the interpreter and versions.

## Lab 02 · Build kinematic intuition

Open the [browser lab](../temel/laboratuvar.md). Calculate the endpoint for `q1=q2=0` and compare with the display. Change q2 to see that it is relative to the first link. Finish when you can convert degrees/radians and explain why this two-link model is not the SO-101.

## Lab 03 · Track a target

```bash
.venv/bin/python examples/01_mujoco_basics.py --target 0.7
```

Read `outputs/joint_tracking.csv`. Change the target to −0.4 and inspect final error. Distinguish simulation time, commanded target and measured angle.

## Lab 04 · Load the SO-101

```bash
.venv/bin/python examples/02_strands_so101.py --render
```

Expect before/after PNGs and six state channels. Change cube color and camera position in your experiment copy. Identify which change affects observations. Finish when you have generated an image and can explain why a mock policy is not a task expert.

## Lab 05 · Create a dataset

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/lab05 --episodes 3 --steps 30
.venv-ml/bin/python examples/04_inspect_dataset.py data/lab05 --expected-episodes 3
```

Expect three episodes, 90 decision rows and camera video. Rerun inspection with `--expected-episodes 4`: it should fail without modifying data. Check metadata rather than counting video files.

## Lab 06 · Read the data back

```bash
.venv-ml/bin/python examples/08_read_dataset.py --root data/lab05 --repo-id local/sim-smoke --index 15
```

Expect `outputs/dataset_frame_15_front.png` and shape `[3,256,256]`. Read the first and last frames separately. Actual decoding is additional evidence beyond a valid schema.

## Lab 07 · Train a tiny model

```bash
.venv/bin/python examples/07_toy_behavior_cloning.py --output outputs/lab07
```

Inspect loss, saved weights and held-out endpoint error. Compare `--steps 100` against 2,000 updates using another output directory. Explain the difference between training loss, held-out error and a constant baseline. This is not VLA training.

## Lab 08 · Hardware and teleoperation

After delivery, follow [power-on](../donanim/ilk-acilis.md) and [teleoperation](../donanim/teleop.md). Produce a device card, calibration record and camera mapping. Check small joint movements, expected directions, gripper opening and stopping. Do not mark this complete before testing physical hardware.

## Lab 09 · Five pilot demonstrations

Run the [real-data recipe](../donanim/veri.md) for five episodes. Watch every video and correct quality problems before training. Record task boundaries, camera visibility and action units. Five pilot episodes are a data-quality check, not a claim of sufficient training coverage.

## Lab 10 · Generate a training command

```bash
.venv-ml/bin/python examples/05_prepare_training.py \
  --root data/lab05 --repo-id local/sim-smoke \
  --output-dir outputs/train/lab10 --steps 20 \
  --batch-size 1 --device cpu --eval-split 0
```

This prints an unexecuted SmolVLA command. Compare `policy.input_features` with metadata and check that no absent camera was invented. Mock-data training only exercises the pipeline.

## Lab 11 · GPU smoke run and fine-tuning

With useful demonstrations, complete the [100-step training recipe](../ogrenme/smolvla.md), inspect saved files, then start a longer run with a separate output directory. Set up the actual GPU environment first. Completion evidence is finite loss, readable data, saved checkpoints and versioned settings; task evaluation is still ahead.

## Lab 12 · Evaluate and improve

Record 20 predefined attempts with one fixed checkpoint. Label every result and summarize the CSV with `06_evaluate_results.py`. Design the next experiment around the largest failure group. Keep final testing independent from training and model selection.

## Lab 13 · Two IK branches

```bash
.venv/bin/python examples/12_planar_ik.py --x 0.22 --y 0.10
```

Inspect both angle solutions, FK reconstruction and Jacobian. Try `(0.32,0)` and `(0.40,0)`. Explain branch merging, singularity and unreachable targets using the [kinematics chapter](../temel/kinematik-ik.md).

## Lab 14 · SO-101 target state machine

```bash
.venv/bin/python examples/09_so101_waypoints.py --output outputs/lab14
```

Inspect three stages, CSV and report. Try `--timeout 0.1 --output outputs/lab14-timeout` to produce a reported failure. Explain measured error, changing reference and timeout. [Controller walkthrough](../simulasyon/denetleyici.md).

## Lab 15 · Episode boundaries and padding

```bash
.venv-ml/bin/python examples/10_action_windows.py \
  data/lab05 --horizon 50 --output outputs/lab15.npz --verify-lerobot
```

Expect 69% padding for 30-frame episodes, with boundary comparisons against LeRobot. Calculate H=10 first, then verify in a new file. Explain why labels must not cross into the next episode and how masked loss is averaged. [Data engineering](../ogrenme/veri-muhendisligi.md).

## Lab 16 · Flow matching arithmetic

```bash
.venv/bin/python examples/11_flow_matching.py
```

Expect MSE 0.025, four ideal Euler steps and masked loss 7.5. Change the example values in a copy and calculate expected results first. Separate flow time from robot time and arithmetic from actual model training. [SmolVLA internals](../ogrenme/smolvla-ic-yapi.md).

## Lab 17 · Build a physics scene

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene drop --output outputs/lab17
.venv/bin/python examples/13_mujoco_playground.py --scene drop --gravity 0 --output outputs/lab17-zero
```

Compare final cube height and contacts. Explain model versus state, why the free joint matters, and why zero gravity leaves this initially stationary cube suspended. [Simulation from scratch](../simulasyon/sifirdan.md).

## Lab 18 · Measure friction

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 0.1 --output outputs/lab18-low
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 1 --output outputs/lab18-high
```

Predict which cube travels farther, then compare horizontal displacement. Keep starting velocity, gravity and duration unchanged. Explain why changing several variables would weaken your conclusion. Continue with [ten experiments](../simulasyon/deneyler.md).

## Lab 19 · Servo, observation and reset

```bash
.venv/bin/python examples/13_mujoco_playground.py --scene servo --target 0.7 --render --output outputs/lab19
```

Inspect angle tracking, RGB and metric depth, then the reset report. Explain why rendering does not itself advance physics, and why resetting state does not undo a change to the model's gravity. Graphics access is needed for this rendering experiment.

## Lab 20 · Inspect a public dataset

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace
```

Record revision, total size, robot type, camera keys and action names. Download using the explicit revision and size cap in the [Hub walkthrough](../ogrenme/huggingface.md), then inspect and decode it. Explain why a SO-100 dataset is not automatically compatible with a SO-101.

## Lab 21 · Learn inside physics

```bash
.venv-ml/bin/python examples/15_first_learning.py --output outputs/lab21
```

Inspect 40 episodes, train/validation/test membership, loss and six test rollouts. Explain teacher actions, train-only statistics, optimizer updates and the hold-start baseline. [First learning loop](../ogrenme/ilk-ogrenme.md).

## Lab 22 · Produce LeRobot data

```bash
.venv-ml/bin/python examples/16_create_lerobot_dataset.py \
  outputs/lab21/demonstrations.csv --root data/lab22
.venv-ml/bin/python examples/04_inspect_dataset.py data/lab22 --expected-episodes 40
```

Inspect the metadata and `ATOLYE_CARD.json`. Explain the two observation values, one action, units and missing cameras. A valid numeric dataset is useful for teaching control; the six-action visual SmolVLA recipe requires a different schema and demonstrations.
