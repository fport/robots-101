# Sources and versions

Reference date: **8 September 2026**. This bilingual workshop uses original explanations and runnable teaching experiments. Primary sources below support API, hardware and model facts; it is not a republication of their complete documentation.

## Sources you supplied

| Source | How it was used |
|---|---|
| [strands-labs/robots](https://github.com/strands-labs/robots) | Main integration; inspected source and installed package |
| [Hashtag Robotics SO-101](https://labs.hashtagrobotics.tr/so-101-robot-kol) | Kit context, leader/follower and accessories |
| [Qwak CDN address](https://cdn-avatars.qwak.ai/HashtagRobotics) | Could not obtain readable content; not used for technical claims |

A failed CDN read does not establish whether the address is a manual, brand asset or another resource. Supplier descriptions and independent test results remain distinct.

## Primary technical references

| Subject | Source |
|---|---|
| Robot design/models | [TheRobotStudio/SO-ARM100](https://github.com/TheRobotStudio/SO-ARM100) |
| SO-101 setup | [LeRobot SO-101](https://huggingface.co/docs/lerobot/en/so101) |
| Installation | [LeRobot installation](https://huggingface.co/docs/lerobot/en/installation) |
| Teleoperation/recording | [Imitation learning guide](https://huggingface.co/docs/lerobot/en/il_robots) |
| Cameras | [Camera guide](https://huggingface.co/docs/lerobot/en/cameras) |
| Camera geometry | [OpenCV calibration tutorial](https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html), [calib3d](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html) |
| Numerical IK | [Modern Robotics 6.2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/) |
| Optimization | [PyTorch AdamW](https://docs.pytorch.org/docs/stable/generated/torch.optim.AdamW.html) |
| Dataset format | [LeRobotDataset v3](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3) |
| Hub downloads | [Hugging Face download guide](https://huggingface.co/docs/huggingface_hub/en/guides/download) |
| Downloaded example | [SO-100 pick-and-place dataset](https://huggingface.co/datasets/lerobot/svla_so100_pickplace) |
| SmolVLA | [Guide](https://huggingface.co/docs/lerobot/en/smolvla), [paper](https://arxiv.org/abs/2506.01844), [base model](https://huggingface.co/lerobot/smolvla_base) |
| Camera mapping | [Rename map](https://huggingface.co/docs/lerobot/en/rename_map) |
| ACT | [Policy guide](https://huggingface.co/docs/lerobot/en/act) |
| Hardware inference | [Rollout](https://huggingface.co/docs/lerobot/en/inference) |
| Timing | [Async](https://huggingface.co/docs/lerobot/en/async), [RTC](https://huggingface.co/docs/lerobot/en/rtc) |
| MuJoCo | [Overview](https://mujoco.readthedocs.io/en/stable/overview.html), [Python](https://mujoco.readthedocs.io/en/stable/python.html) |
| Model authoring | [Modeling](https://mujoco.readthedocs.io/en/stable/modeling.html), [XML reference](https://mujoco.readthedocs.io/en/stable/XMLreference.html) |
| Strands simulation | [Overview](https://strands-labs.github.io/robots/simulation/overview/) |
| Strands recording | [Recording source](https://github.com/strands-labs/robots/blob/main/docs/recording.md) |
| Strands local policy | [LeRobot local](https://github.com/strands-labs/robots/blob/main/docs/policies/lerobot-local.md) |
| Strands training | [Training overview](https://github.com/strands-labs/robots/blob/main/docs/training/overview.md) |
| Environment manager | [uv](https://docs.astral.sh/uv/) |
| Website | [MkDocs](https://www.mkdocs.org/), [Material](https://squidfunk.github.io/mkdocs-material/), [static i18n](https://ultrabug.github.io/mkdocs-static-i18n/) |

## Pinned baseline

Flowcharts use [Mermaid](https://mermaid.js.org/intro/) **11.17.2**, with its local bundle and MIT license in `docs/assets/vendor/`. [Theme settings](https://mermaid.js.org/config/theming.html) follow the neon-green light/dark palette. This presentation layer does not run simulation or model training.

| Component | Workshop baseline |
|---|---|
| Python | 3.12.12 on macOS arm64 |
| MkDocs / Material | 1.6.1 / 9.7.7 |
| mkdocs-static-i18n | 1.3.1 |
| Strands Robots | 0.5.1 |
| MuJoCo | 3.12.0 |
| LeRobot | 0.6.1 |
| PyTorch / torchvision / torchcodec | Exact ML snapshot in `constraints-ml-macos.txt` |

The requirements files pin main dependencies. The constraints files capture this Mac's transitive environment; do not apply its platform wheel choices blindly to Linux/CUDA. Save your own resolved `uv pip freeze` output.

Inspected source commits:

- Strands Robots: [`82be6e684314c20a2778c4927f63f2d737795b43`](https://github.com/strands-labs/robots/tree/82be6e684314c20a2778c4927f63f2d737795b43)
- LeRobot: [`2774d9bddcbbda50e697e162e89e7eaada8d7105`](https://github.com/huggingface/lerobot/tree/2774d9bddcbbda50e697e162e89e7eaada8d7105)
- SO-ARM100 asset downloaded through `robot_descriptions`: `63eede5a636e548eb8f2854e558bd343c21db9f7`
- Downloaded Hub dataset: `728583b5eaf9e739a7f119e2def466fa1d552402`

The inspected GitHub LeRobot source identified a 0.6.2 development version while execution used published 0.6.1. Installed source and CLI help were also checked to avoid assuming unreleased behavior exists locally.

## Updating safely

Keep the working environment. Test new packages in a separate environment: physics, SO-101 render, dataset recording/reading, schema validation, then short training. Update version snapshots and the validation record together.

Pin model and dataset revisions separately. Pinning a Python package does not pin Hub `main`. Keep data, base model and your trained checkpoint identities as separate experiment fields. Actual test scope is listed in the [validation record](basla/dogrulama.md).
