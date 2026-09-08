# Imitation learning, ACT and VLA

You can create behavior through explicit control rules, imitation of demonstrations, or interaction guided by rewards. This workshop begins with **imitation learning**: learn an expert's action from the observation available at the time.

```text
observation = camera images + joint state + task
target      = expert action, or a sequence of future expert actions
model       = a learned mapping from observation to target
```

In a simple regression example the loss can be mean squared prediction error. Actual VLA architectures and objectives differ; they do not all predict six angles from one image with a single MSE loss.

## Train a small model first

For the full physics → demonstration → training → rollout path, start with [your first learning experiment](ilk-ogrenme.md). There is also a lighter NumPy exercise:

```bash
.venv/bin/python examples/07_toy_behavior_cloning.py
```

It generates target positions and joint angles from a two-link arm's known forward kinematics, then trains a small network to map `(x,y)` to two joint angles. It uses 1,500 training samples and 300 separate test samples within the same sampling bounds. Outputs are `outputs/toy-bc/loss.csv`, `metrics.json` and `policy.npz`.

Compare endpoint error with the constant mean-pose baseline. This exercise has no camera, language, motors or MuJoCo dynamics. It teaches the learning loop. The data use one elbow solution branch: averaging two valid but different joint solutions can produce an invalid result. This is a small example of why multimodal demonstrations need care.

## ACT as a baseline

ACT predicts action sequences and provides an imitation-learning baseline for a limited task. Its claim differs from general language-conditioned VLA behavior. A working ACT policy on the same data is useful evidence about the camera, data and control pipeline before comparing pretrained visual-language representations. Model size alone does not explain success. [LeRobot ACT](https://huggingface.co/docs/lerobot/en/act)

## Vision–Language–Action

Vision supplies images, language specifies the task, and action is the robot control output. Robot state can also condition the prediction. The main output is a control sequence; describing visible objects in chat is a different task.

The SmolVLA paper presents a compact VLA of roughly 450 million parameters and an asynchronous execution approach. Parameter count does not guarantee success on your task or real-time execution on your computer. [SmolVLA paper](https://arxiv.org/abs/2506.01844)

| Process | What happens? | Workshop role |
|---|---|---|
| Pretraining | Learn starting weights from broad data | We use an existing starting model |
| Fine-tuning | Adapt those weights using your demonstrations | Main SmolVLA training path |
| Inference | Compute actions with fixed weights | Simulation or hardware rollout |
| Evaluation | Measure success and failure under a protocol | Separate test attempts |

`lerobot/smolvla_base` does not automatically know your calibration or table layout. Adaptation and matching input/output contracts remain necessary.

## Distribution shift and recovery

An imitation policy may work in states visited by the expert. A small mistake moves the object into an unfamiliar state, and subsequent errors accumulate. Low training loss therefore differs from high task success.

Start with clean successful demonstrations. Later, teach deliberate recovery from common small deviations. This requires a correct teacher action in the difficult state; adding indecisive or arbitrary failed motion teaches something else. [Advanced work](ileri.md) explains human intervention and reinforcement learning.
