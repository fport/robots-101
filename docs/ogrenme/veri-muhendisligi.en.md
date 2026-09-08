# Data engineering: time, labels and splits

A readable Parquet file can still teach the wrong relationship. Image/action timing, episode boundaries and independent test conditions define the learning problem. Here the 3-episode, 90-frame smoke recording lets you inspect these relationships. It contains pipeline exercises, not expert grasping demonstrations.

## 1. Define one decision

```text
o_t     = observation available before the decision
a_t     = action sent using that observation
o_(t+1) = observation after applying the action and advancing time
```

Behavior cloning learns `o_t → a_t`. Pairing `o_(t+1)` with `a_t` may reveal information unavailable at decision time. Pairing a frame with an earlier action teaches another delay relationship. Inspect the recording loop's read → decide → send → record order; column names alone cannot establish timing.

The [controller CSV](../simulasyon/denetleyici.md) separates `q_before`, `command` and `q_after`. With physical teleoperation, the leader request may differ from the limited command actually sent to the follower. Record which one is the training label, especially when applying `max_relative_target`.

## 2. Camera delay in numbers

At 30 Hz a decision interval is about 33.3 ms. A camera image that is 100 ms old is roughly three decisions behind. At an endpoint speed of 0.10 m/s, that delay corresponds to 1 cm of movement, enough to affect a small-object grasp.

Measure exposure/capture time, frame retrieval time, state read time and command send time separately where possible. Two cameras advertising 30 FPS are not necessarily synchronized. USB/video queues can return old frames. Slowly open and close the gripper, then compare image changes with state/action traces. Do not shift the whole dataset by three frames without measurement: a fixed offset cannot fix variable latency.

## 3. Target, delta and measured movement

Suppose `q_t=0.10 rad`, the sent target is `a_t=0.16 rad`, and the next measurement is `q_(t+1)=0.12 rad`:

| Representation | Value | Meaning |
|---|---|---|
| Absolute target | 0.16 rad | Position the servo tries to reach |
| Target relative to current state | 0.06 rad | Requested displacement from the current measurement |
| Observed movement | 0.02 rad | Movement actually completed during the interval |

Your runtime must implement the representation used for labels. Six output numbers do not prove the right meaning or unit. Include joint order, reference, units and gripper range in the dataset card.

Normalization adds a numerical transform. With mean `0.10` and standard deviation `0.05`, a raw target of `0.16` becomes `1.2`. Do not send `1.2` as radians: invert the correct transform first. Normalization cannot repair the wrong physical unit.

## 4. Future action windows

For a horizon `H=50`, an observation at time `t` is paired with:

```text
[a_t, a_(t+1), ..., a_(t+49)]
```

At 30 Hz the first-to-last timestamp difference is `49/30 ≈ 1.633 s`; executing all 50 commands at that frequency occupies about `50/30 ≈ 1.667 s`. State which duration you mean.

An episode with 30 frames never has 50 real future actions. LeRobot clamps out-of-episode indices to the boundary sample and marks padding, preventing actions from the next demonstration from leaking in. [Dataset reader](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/datasets/dataset_reader.py)

## 5. Work out the padding

For a four-frame episode and `H=3`:

| Start | Window | `action_is_pad` |
|---|---|---|
| 0 | a0, a1, a2 | false, false, false |
| 1 | a1, a2, a3 | false, false, false |
| 2 | a2, a3, a3 | false, false, true |
| 3 | a3, a3, a3 | false, true, true |

Repeated boundary actions preserve tensor shape; they are not new demonstrations. `true` means padding. Reversing that interpretation excludes useful targets from loss.

For 30 frames and horizon 50, real slots total `30+29+...+1=465`. There are `30×50=1500` total slots, so `1035/1500=69%` are padding. Three episodes of the same length give the same fraction.

## 6. Run it on the recording

Use the root of a recording you created; this workspace's verified root is:

```bash
.venv-ml/bin/python examples/04_inspect_dataset.py data/sim-smoke-verified
.venv-ml/bin/python examples/10_action_windows.py \
  data/sim-smoke-verified --horizon 50
```

Expected shapes: actions `[90,50,6]`, mask `[90,50]`, states `[90,6]`, padding fraction `0.69`. The output is `outputs/action-windows.npz`. Try another horizon with a new output path:

```bash
.venv-ml/bin/python examples/10_action_windows.py \
  data/sim-smoke-verified --horizon 10 \
  --output outputs/action-windows-h10.npz
```

For `H=10`, valid slots are `21×10+9+8+...+1=255` out of 300: 15% padding. Lower padding alone does not imply better task success.

The script normally reads small Parquet tables into memory without normalization. It is an educational inspection tool rather than a replacement training reader. You can compare the first and last sample of every episode with the real LeRobot reader, including PyAV decoding at these boundaries:

```bash
.venv-ml/bin/python examples/10_action_windows.py \
  data/sim-smoke-verified --verify-lerobot \
  --output outputs/action-windows-checked.npz
```

All 6 boundary samples matched for the verified three episodes.

## 7. The loss denominator matters

```text
loss = sum of squared errors over valid elements
       / (valid time steps × actual action dimensions)
```

Take squared errors `[1,4]` and `[9,16]` at two valid steps with two action dimensions. The third step is padding. Correct loss is `30/4=7.5`; dividing by all three steps gives `30/6=5`, making the same predictions look better just because padding increased. The inspected SmolVLA final loss divides by valid elements; intermediate diagnostic logs can use different reductions. [Loss implementation](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/modeling_smolvla.py)

## 8. Split by the claim you want to test

Neighboring frames and their overlapping action windows are very similar. Random frame splits can place near duplicates in training and validation. Episode splitting is a minimum starting point. For a stronger claim, group by recording day, object instance, starting region or camera arrangement.

An illustrative 100-episode plan is 70 for training, 15 for model selection and 15 for final testing. These are not universal ratios. Changing settings after checking the last 15 uses final test information. `dataset.eval_split` does not automatically create day- or object-based independence.

Ideally, compute normalization statistics from training data only. Inspect how existing metadata statistics were created; do not assume the split flag recomputes them. Version preprocessing statistics and episode membership alongside the model.

## 9. Diversity is different from volume

A hundred repetitions from one position do not cover a hundred different starting positions. Map left/center/right, near/far, grasp orientations and controlled lighting changes, then count unfilled combinations. Recovery demonstrations need correct actions that finish the task from a deviation. Failed episodes remain useful for analysis, but their training target must be chosen deliberately.

Finish this chapter with an action contract, a timing inspection, padding measurements, grouped split lists and video quality notes. Those make training results interpretable.
