# What should I know, and when?

Running commands is enough to start. Building and improving your own task requires understanding **mechanics → measurement → control → data → learning → evaluation**. Here, “hero” means knowing which measurement to make when that chain fails, not memorizing every robotics paper.

Do not try to learn everything during week one. If the vocabulary itself is new, read [start from zero](sifirdan.md). Progress below is determined by evidence, not a fixed calendar.

## 1. Before delivery: run an experiment

Identify your Python environment, working directory, file paths and units. You need not be a Python expert, but should understand why system `python` might see different packages from `.venv/bin/python`.

For any command, answer: which robot/joint; position, velocity or torque; which units; how much time advances; what is measured afterward; and what must hold for success, for how many samples?

**Evidence:** run [target tracking](../simulasyon/denetleyici.md) and explain one CSV row. If `command`, `q_before`, `q_after` and `goal` seem interchangeable, revisit this stage.

## 2. Task design: geometry and observation

“Pick up the red cube” does not yet specify a control problem. Define its starting region, visibility, approach direction, closure timing and placement success.

Solve the [two-link IK example](../temel/kinematik-ik.md). Explain why five arm joints cannot independently realize every six-dimensional pose. Learn why one pixel is not a 3D point in [camera geometry](../donanim/kamera-kalibrasyonu.md).

**Evidence:** a one-page task contract with start, objects, observations, action units, completion and timeout. Use the [capstone template](../pratik/proje.md).

## 3. Physical demonstrations

Motor IDs, servo calibration, camera calibration and model normalization are distinct. Verify leader movement produces the intended follower direction and range.

Record five pilot episodes, review every video and inspect state/action traces. A hidden object or delayed image needs a recording fix before model scaling. [Data engineering](../ogrenme/veri-muhendisligi.md) explains these checks.

**Evidence:** a device/camera record that lets you rebuild the arrangement another day, plus reasons for rejected episodes.

## 4. First training: understand the objective

Learn tensor, batch, normalization, action chunk, mask, loss, optimizer, checkpoint and validation. You need to know which examples and scale enter the loss, even before proving every derivative.

Start with [the small CPU learning loop](../ogrenme/ilk-ogrenme.md), then calculate the [flow matching example](../ogrenme/smolvla-ic-yapi.md) by hand. Choose one hypothesis from [training experiments](../ogrenme/egitim-deneyleri.md), such as whether a wrist camera improves closure. Do not simultaneously change camera, learning rate and dataset size in your first comparison.

**Evidence:** two comparable runs with dataset revision, checkpoint, losses and rollout outcomes. Training completion and task success are separate entries.

## 5. Advanced work: measure limitations

Contact modeling, system identification, domain randomization, advanced IK, task planning, asynchronous inference and RL become useful when a measured bottleneck requires them. ROS 2 is not a prerequisite for this workshop's basic simulation/LeRobot loop.

**Evidence:** tests showing where behavior fails outside training conditions, and a targeted improvement experiment. Report conditions, counts and failure types instead of “sometimes works.”

## Deeper reading order

| Chapter | Question |
|---|---|
| [Kinematics and IK](../temel/kinematik-ik.md) | How do tip targets become joint angles? |
| [Measured control](../simulasyon/denetleyici.md) | How do I know movement completed? |
| [Camera geometry](../donanim/kamera-kalibrasyonu.md) | How do robot and camera describe the same point? |
| [Data engineering](../ogrenme/veri-muhendisligi.md) | Which times belong to one training example? |
| [SmolVLA internals](../ogrenme/smolvla-ic-yapi.md) | What does its loss teach? |
| [Training experiments](../ogrenme/egitim-deneyleri.md) | Why can low loss coexist with poor behavior? |
| [Worked questions](../pratik/cozumlu-sorular.md) | Can I explain this independently? |

## Scope

Local examples include actual SO-101 asset tracking, image recording, dataset reading and small learning experiments. End-to-end **SmolVLA object grasping** has not been validated. New GPU/hardware experiments should be added to the [validation record](dogrulama.md). Detailed reading prepares you to conduct those experiments; it cannot replace them.
