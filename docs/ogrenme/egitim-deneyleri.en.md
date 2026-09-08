# Treat training as an experiment

Choosing a model and typing `steps=20000` does not define an experiment. Record the hypothesis, constants, checkpoint selection rule and final evaluation before running it. The numbers here illustrate reasoning; they are not measured SmolVLA training times, VRAM requirements or guaranteed success rates. Commands live in the [training recipe](smolvla.md).

## 1. Steps, batches and epochs

Suppose training has 24,000 decision frames, batch size 8 and 20,000 optimizer updates. On one GPU with one update per batch, sample uses total `8×20,000=160,000`, approximately `160,000/24,000=6.67` epoch equivalents. Sampling, drop-last and episode filters mean each frame need not appear equally often. Overlapping action windows are also not independent demonstrations.

Effective batch is conceptually `batch per device × device count × accumulation steps`. This is not permission to invent an unsupported CLI flag; the workshop generator uses one device and a direct batch size. Halving batch size at fixed update count halves sample uses. It changes the experiment as well as memory.

## 2. Learning rate and warmup

Learning rate scales how gradients affect weight updates. Too large can destabilize learning; too small can adapt slowly within the budget. AdamW also uses moving moment estimates and decoupled weight decay. [PyTorch AdamW](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html)

Warmup increases learning rate early; decay describes its later schedule. Inspected SmolVLA defaults include 1,000 warmup and 30,000 decay steps. Your checkpoint configuration and logged learning rate are authoritative. With those defaults a 100-step smoke run remains inside warmup, useful for testing the pipeline but insufficient to judge long-term learning. Record the schedule and total updates whenever you change learning rate. [Configuration](https://github.com/huggingface/lerobot/blob/2774d9bddcbbda50e697e162e89e7eaada8d7105/src/lerobot/policies/smolvla/configuration_smolvla.py)

## 3. Break memory into components

Training memory includes weights, gradients of trainable parameters, optimizer states, activations, images and temporary workspaces. An illustrative 100 million trainable FP32 parameters use about 400 MB for weights, 400 MB for gradients and 800 MB for two Adam moment arrays: 1.6 decimal GB before activations and other components. This is not a measured SmolVLA requirement. Precision and optimizer implementation change the calculation.

Two 512×512 RGB cameras with batch 8 in float32 occupy `8×2×3×512×512×4=50,331,648` bytes, or 48 MiB, just for the raw image batch. Internal activations can be much larger.

On out-of-memory errors, first reduce batch size. Verify supported precision and activation-checkpointing options against your version. Removing a camera changes information available to the policy, not just infrastructure cost. Record whether the failure occurred during loading, preprocessing, forward or backward.

## 4. Write a minimal experiment card

Use `templates/experiment.md`:

| Field | Example |
|---|---|
| Hypothesis | A wrist camera reduces grasp-closure errors |
| Data version | `pick-v2`, with episode lists and units |
| Constants | Base checkpoint, task, split groups, seed and budget |
| Variable | Add wrist imagery to front imagery |
| Primary metric | Predefined pick-and-place success |
| Diagnostics | Misses, drops, wrong placement, latency and losses |
| Result | Counts, uncertainty and failed-video paths |

Changing one factor makes first comparisons easier to interpret. More advanced experiments can examine interactions; changing five settings at once makes attribution difficult.

## 5. Four initial runs

| Run | Purpose | Evidence before continuing |
|---|---|---|
| A: Read data | Check schema, video, units and masks | An inspected batch is correct |
| B: Short training | Test forward/backward and saving | Finite loss and reloadable output |
| C: Reference training | Establish task performance | Rollouts under a fixed protocol |
| D: Targeted change | Address the largest failure group | Comparison under C's test conditions |

In B, deliberately overfitting a few samples can reveal whether the training signal flows. It diagnoses labels and optimization; memorizing those samples is not generalization. Also compare against the starting checkpoint rather than assuming fine-tuning helped.

## 6. Falling loss, poor robot behavior

**Check the contract first:** checkpoint, camera keys, RGB/BGR, joint order, units and inverse normalization. More updates cannot fix a deployment mapping error.

**Then check timing:** image age, inference latency, control rate and executed chunk length. Compare stationary and changing scenes to test a latency hypothesis.

**Then check coverage:** compare training and rollout starting conditions. A cube taught only at the center provides weak evidence for performance at the table edge. Count demonstrations in the failed region.

**Then investigate learning:** worsening validation with improving training suggests overfitting. If both remain poor, inspect labels, scaling, learning rate, trainable parameters and variation. Loss curves alone do not uniquely identify any one cause.

## 7. Turn symptoms into experiments

| Symptom | Initial hypothesis | Separating experiment |
|---|---|---|
| First command moves in the wrong direction | Ordering, sign or unit mismatch | Match a small single-joint command with state |
| Reaches object but closes early | Visibility or timing | Align camera/action traces around closure |
| Always reaches one location | Insufficient position coverage | Map training positions and test a new region |
| Grasps but drops during transport | Contact or transport commands | Score lift and transport separately |
| Works in sim, fails on hardware | Unit, visual or dynamics gap | Verify contract, then vary visual/dynamic factors separately |
| Great validation, poor next-day results | Leakage or changed conditions | Hold out a recording day |
| Loss suddenly becomes NaN | Data scale or numerical error | Save the first bad batch and inspect finite values/ranges |

These are hypotheses, not automatic diagnoses. Produce evidence that could support or refute each one.

## 8. Checkpoint selection and final test

The last checkpoint is not necessarily best. Choose using the predefined validation protocol. If physical tests are expensive, shortlist candidates before comparison. Reusing final test conditions during selection transfers test information into settings.

Suppose A succeeds 14/20 times and B 16/20. Reporting only 70% → 80% hides uncertainty from small samples. The [evaluation tool](degerlendirme.md) reports counts and Wilson intervals. Matched initial conditions and repeated trials help; interval overlap alone is not a formal paired comparison test.

Define exclusions before viewing outcomes. If an initial condition is invalid, record it and report the excluded count. Do not remove inconvenient failures after seeing them.

## 9. Practical reproducibility

Seeds help, but GPU kernels, library revisions, timing and physical contact can prevent bit-for-bit agreement. Tie episode lists, base-model revision, command, package versions, logs, preprocessing files, checkpoint and test CSV to one experiment ID. Copying only a weights file may omit the runtime contract.

You are finished when someone else can tell what you trained, on which data, with which settings, and what the independent test showed. The next experiment should have a reason you can state in one sentence.
