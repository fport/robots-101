# Command notebook

Run from the project root. See [installation](../basla/kurulum.md) for environments and [hardware setup](../donanim/ilk-acilis.md) before motor commands. Pick fresh output directories for new experiments.

## Read or build the site

```bash
make serve
make build
```

The server uses `http://127.0.0.1:8000`; English is under `/en/`. The build writes `site/` for static hosting. Building locally does not publish a site.

## Physics and SO-101

```bash
make doctor
make physics
make sim
.venv/bin/python examples/13_mujoco_playground.py --scene drop --output outputs/drop-run
.venv/bin/python examples/13_mujoco_playground.py --scene slide --friction 0.1 --output outputs/slide-run
```

The playground and single-hinge example run physics without a window. SO-101 needs its initial asset download; PNG output needs graphics. On macOS use `mjpython` for a live viewer:

```bash
.venv/bin/mjpython examples/13_mujoco_playground.py --scene servo --viewer --output outputs/servo-live
```

## Record, inspect and read

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/new-smoke
.venv-ml/bin/python examples/04_inspect_dataset.py data/new-smoke --expected-episodes 3
.venv-ml/bin/python examples/08_read_dataset.py --root data/new-smoke --repo-id local/sim-smoke
```

Recording needs graphics and will not overwrite an existing dataset root.

## Hub data and your first model

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace
.venv-ml/bin/python examples/15_first_learning.py --output outputs/first-learning-run
.venv-ml/bin/python examples/16_create_lerobot_dataset.py \
  outputs/first-learning-run/demonstrations.csv --root data/teaching-run
.venv-ml/bin/python examples/04_inspect_dataset.py data/teaching-run --expected-episodes 40
```

The Hub command inspects listing/metadata by default. Use the [download recipe](../ogrenme/huggingface.md) for pinned revisions and size limits. The CPU teaching model is a one-hinge policy; it is not SmolVLA. Another small NumPy exercise is:

```bash
.venv/bin/python examples/07_toy_behavior_cloning.py --output outputs/toy-run-02
```

## Generate SmolVLA training

```bash
.venv-ml/bin/python examples/05_prepare_training.py \
  --root data/so101-pick-v1 --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/smolvla-v1 \
  --save-command outputs/commands/train-v1.sh
```

This saves a command without starting training. Once data and device are ready, activate the ML environment and run `bash outputs/commands/train-v1.sh`. Read the [training chapter](../ogrenme/smolvla.md) before that step.

## Report actual attempts

```bash
.venv/bin/python examples/06_evaluate_results.py outputs/evaluation.csv
```

Populate the CSV with real attempts using the template header. Template rows are illustrative.

## Check help and versions

```bash
.venv-ml/bin/lerobot-train --help
.venv-ml/bin/lerobot-record --help
.venv-ml/bin/lerobot-rollout --help
uv pip freeze --python .venv-ml/bin/python
make check
.venv-ml/bin/python -m unittest discover -s tests -v
```

If a GitHub `main` flag is absent locally, inspect the version difference. Preserve the working environment and test upgrades separately.
