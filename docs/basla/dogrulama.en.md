# Validation record

Reference date: **8 September 2026**, machine **macOS 26.3.1 / Apple Silicon arm64**, Python **3.12.12**. A completed check establishes only the scope shown below. Physical hardware and full GPU training remain unverified.

## Executed experiments

| Experiment | Observed result | What it establishes |
|---|---|---|
| One-joint MuJoCo tracking | 3 simulated seconds; 0.7 rad target; error about 2.22e−16 rad | Physics and target tracking for this simple model |
| Strands SO-101 | 30 control steps, zero action errors, before/after PNGs | Asset, API, physics and rendering pipeline |
| Live SO-101 viewer | macOS `mjpython --viewer --steps 30` opened and closed | Local interactive viewer path |
| Simulation recording | 3 episodes × 30 frames = 90 | Image/action dataset writing and episode boundaries |
| Parquet validation | 3 episodes, 90 frames, no errors | Schema, ordering and timestamp checks |
| LeRobot/PyAV read | `[3,256,256]` image tensor and PNG | Actual video decoding and indexed access |
| Measured SO-101 tracking | 3/3 targets, 121 control steps, 2.42 simulated seconds | Transitions based on all six measured errors |
| Tracking timeout | Failure report/CSV and exit 1 with 0.1 s timeout | Failed experiments are also reported |
| Action windows | `[90,50,6]`, 69% padding | Labels preserve episode boundaries |
| LeRobot window comparison | 6/6 first/last boundary samples matched | Actions and masks agree with the real reader |
| Flow arithmetic | MSE 0.025, ideal Euler path, masked loss 7.5 | Signs, interpolation and loss reduction |
| Two-branch planar IK | FK and finite-difference Jacobian checks passed | Teaching model's mathematical consistency |
| NumPy behavior cloning | 1,500 training / 300 test points; mean endpoint error about 0.346 cm | Small kinematic regression learning |
| Mean-pose baseline | Mean endpoint error about 12.05 cm | Comparison for the NumPy model |
| Playground gravity | Cube settles near z=0.02497 m; with zero gravity remains at 0.60 m | Free-body motion and contact in this scene |
| Playground friction | Travel about 0.3256 m at μ=0.1, 0.02976 m at μ=1 | Controlled friction comparison |
| Playground servo/push/reset | 0.7 rad target tracking, force-driven displacement and zero reset time | Command, force and state-reset examples |
| RGB and depth render | 640×480 RGB plus metric depth array | Local graphics path; driver depth caveat below |
| Public Hub download | 470.117 MB, pinned revision, 50 episodes / 19,631 frames | Complete downloaded dataset and metadata |
| Public dataset decoding | Top and wrist cameras each `[3,480,640]` | Actual AV1 video decoding through PyAV |
| First physics learning | 40 episodes / 4,000 rows; 28 train, 6 validation, 6 test | Teacher → training → held-out physics rollout |
| Learned hinge / baseline | 6/6 versus 0/6; mean errors 0.01848 / 0.61127 rad | Comparison within this small teaching distribution |
| Numeric LeRobot conversion | 40 episodes / 4,000 rows; integrity check passed | CSV → local LeRobot numeric data |
| Training preparation | Command generated from real metadata | Feature configuration and CLI preparation |
| Tool tests | ML 12/12 passed; simulation 9 passed and 3 ML-only skips | Data contracts, scalar storage, commands, reports, episode boundaries and IK |
| Strict bilingual build | 43 Turkish + 43 English chapters; 49 navigation translations | Complete translation coverage and documented example flags |
| Chrome checks | 87 HTML link/anchor checks and 86 mobile content pages | Both-language search, calculators, theme, solutions and shared progress; no JavaScript runtime errors |
| Mermaid flowcharts | 12 diagrams across six topics in both languages | Rendering with external requests blocked; light/dark themes and mobile keyboard scrolling |

The browser report records an existing language integration issue under `known_resource_warnings`: Material 9.7.7 looks for `sitemap.xml` below the translated article URLs supplied by static-i18n 1.3.1 and receives 404s. The combined sitemap is at the site root. These requests do not affect diagram rendering; switching languages on the same article is tested separately. All other resource failures or JavaScript errors fail the check.

The NumPy result of 100% below 2 cm applies only to 300 kinematic points within the same sampling bounds. The hinge result of 6/6 is also a small teaching experiment, not SO-101 grasping or VLA performance. Flow arithmetic does not train a model. A numeric one-hinge dataset has no camera observations; its one-action field reads as a scalar tensor in this LeRobot version.

The Hub dataset is **SO-100**, not automatically SO-101 compatible. Its revision is `728583b5eaf9e739a7f119e2def466fa1d552402`. Local artifacts include `data/hub-so100-verified`, `data/teaching-hinge-verified`, `outputs/first-learning-verified` and the playground outputs. These large reproducible directories are excluded from version control.

## Environment details

Restricted graphics initially prevented rendering. With graphics access, rendering and recording completed; recording now tests the camera before creating data. On this Mac the OpenGL driver reports missing `ARB_clip_control`, which can limit depth accuracy. The saved depth array is educational output, not a calibrated real depth sensor.

TorchCodec could not load shared FFmpeg dependencies. PyAV was explicitly used and verified. Package snapshots are in `constraints-docs-sim-macos.txt` and `constraints-ml-macos.txt`.

With 30 Hz control and a 0.002 s physics step, the Strands 30-step run reported about 1.02 simulated seconds because of substep rounding. Consider this when interpreting recorded time versus simulated physical time.

## What has not been executed

- Physical SO-101 connection, calibration, teleoperation or real-camera demonstration collection.
- Downloading full SmolVLA weights and running its forward/backward or GPU fine-tuning.
- Measuring a trained SmolVLA policy's task success in simulation or on hardware.
- Provisioning paid GPUs, uploading datasets/models or publishing the site publicly.

These steps have recipes, but their test status differs from the executed local examples.

## Repeat the checks

```bash
make check
.venv-ml/bin/python -m unittest discover -s tests -v
```

The docs/simulation environment skips tests requiring LeRobot/Parquet. The ML environment includes them. Checks cover invalid dimensions, missing cameras, insufficient splits, timestamp/action corruption, scalar storage, evaluation records, episode leakage and IK boundaries.

The bilingual site is built with MkDocs strict validation. Browser checks require `requirements-test.txt`, local Chrome and a running `make serve`:

```bash
.venv/bin/python scripts/check_site.py
```

The current report and screenshots are written to `outputs/site-check/`. The browser uses an isolated test profile. Record new platform/device results separately rather than treating this Mac's results as verification of a different GPU or delivered kit.
