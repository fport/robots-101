# Installation and your first 30 minutes

Run commands from the project root, currently `/Users/furkanportakal/www/robots`. Shell `$VARIABLE` references are part of commands, not prompt characters to remove. If the terminal itself is unfamiliar, read [start from zero](sifirdan.md) first.

## 1. Open the guide

If `.venv` is already prepared:

```bash
cd /Users/furkanportakal/www/robots
make serve
```

Open **http://127.0.0.1:8000** and choose Türkçe or English in the header. Stop a server you launched with `Ctrl+C`. If the port is occupied, use `.venv/bin/mkdocs serve --dev-addr 127.0.0.1:8001`. The default listens only on this computer.

## 2. Install on a clean machine

Check `uv --version`; if missing, follow [official installation](https://docs.astral.sh/uv/getting-started/installation/). You do not need to replace system Python.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-docs.txt -r requirements-sim.txt
.venv/bin/python examples/00_doctor.py
.venv/bin/mkdocs serve --dev-addr 127.0.0.1:8000
```

uv may download Python 3.12 when it is unavailable locally. This workshop was tested with 3.12; do not assume system Python 3.14 behaves identically. Recipes target macOS/Linux. Windows/WSL simulation and USB passthrough have not been validated here.

## 3. Run real physics

Open a second terminal while the documentation server remains running:

```bash
.venv/bin/python examples/01_mujoco_basics.py
```

Expect approximately 3 simulated seconds, target 0.7 rad and error below 0.02 rad. `outputs/joint_tracking.csv` contains time, measured angle and target. No robot asset or graphics window is required.

=== "macOS viewer"

    ```bash
    .venv/bin/mjpython examples/01_mujoco_basics.py --viewer
    ```

=== "Linux desktop viewer"

    ```bash
    .venv/bin/python examples/01_mujoco_basics.py --viewer
    ```

The macOS passive viewer requires `mjpython` for its main-thread arrangement. PNG rendering is a separate path. [MuJoCo viewer](https://mujoco.readthedocs.io/en/stable/python.html#passive-viewer)

For a more gradual introduction, follow [simulation from scratch](../simulasyon/sifirdan.md) and [ten experiments](../simulasyon/deneyler.md).

## 4. Load SO-101

```bash
.venv/bin/python examples/02_strands_so101.py --render
```

For a live Mac window: `.venv/bin/mjpython examples/02_strands_so101.py --viewer --steps 900`.

The first run downloads robot assets; later runs use the cache. Expect state output, a rollout report and `outputs/so101_before.png` / `so101_after.png`. The mock policy is not expected to grasp the cube. If downloading fails, inspect the first network error rather than treating it as a kinematics problem.

## 5. Create the separate ML environment

This downloads larger dependencies and is optional for reading/basic physics:

```bash
uv venv --python 3.12 .venv-ml
uv pip install --python .venv-ml/bin/python -r requirements-ml.txt
.venv-ml/bin/python examples/00_doctor.py
```

On a CUDA machine, first read [compute setup](../ogrenme/hesaplama.md). PyTorch, torchvision, TorchCodec and FFmpeg compatibility matters. This requirements file does not install an NVIDIA driver.

## Project directories

| Path | Contents |
|---|---|
| `docs/` | Turkish `.md` and English `.en.md` pages |
| `models/` | Runnable teaching MJCF scenes |
| `examples/` | Python exercises |
| `requirements-*.txt` | Pinned primary dependencies |
| `constraints-*.txt` | Full machine-specific dependency snapshots |
| `data/` | Local datasets |
| `outputs/` | Images, CSV, reports, commands, checkpoints |
| `.cache/` | Local asset/model/download caches |
| `site/` | Generated bilingual static site |

Build with `make build`. To serve the built output, use `.venv/bin/python -m http.server 8000 --directory site --bind 127.0.0.1`. Opening through `file://` can break search and directory links.
