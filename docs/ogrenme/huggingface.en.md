# Hugging Face: find, download, read and use data

A **dataset** contains examples. A **model repository** contains learned weights and configuration. Hugging Face Hub hosts both; their repository types differ. `lerobot/smolvla_base` is a model, while `lerobot/svla_so100_pickplace` is a dataset.

## 1. A robot video is not automatically training data

A video does not reveal the motor commands that produced it. Imitation learning needs a relationship between images, measured state, actions, time and task. A Robotics tag does not prove compatibility with your arm.

Read the dataset card for robot type, task, cameras, license and collection method. Then inspect `meta/info.json` for format version, FPS and feature shapes. Do not infer an undocumented action unit with certainty from the numbers alone.

## 2. Inspect before downloading

Prepare the [ML environment](../basla/kurulum.md). This command fetches the repository listing and at most a small `meta/info.json`:

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace
```

The inspected revision on 8 September 2026 was `728583b5eaf9e739a7f119e2def466fa1d552402`: about 470.12 MB, 50 episodes, 19,631 frames, 30 FPS, and `top`/`wrist` cameras. Its robot type is SO-100. We do not relabel it SO-101 data. [Source dataset](https://huggingface.co/datasets/lerobot/svla_so100_pickplace)

Inspection can cache small metadata files; it does not mean zero network use. It does not download the large videos.

## 3. Download a metadata preview

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace \
  --mode metadata --root data/hub-preview --max-mb 5
```

This directory is for schema inspection, not training. Use a different root for the complete snapshot; existing directories are refused to preserve prior work.

## 4. Download a pinned snapshot

```bash
.venv-ml/bin/python examples/14_hub_dataset.py lerobot/svla_so100_pickplace \
  --revision 728583b5eaf9e739a7f119e2def466fa1d552402 \
  --mode download --root data/hub-so100 --max-mb 500
```

The script checks selected file sizes before downloading. The default 250 MB ceiling is too small here, so 500 MB is explicit. A requested revision is resolved to a commit, used for downloads and written to `ATOLYE_DOWNLOAD.json`. The Hub APIs distinguish dataset repositories using `repo_type="dataset"` and support revisions/file filters. [Hub downloads](https://huggingface.co/docs/huggingface_hub/en/guides/download)

In this workspace, the complete verified copy is already at **`data/hub-so100-verified/`**. You can use it without downloading again. Do not assume that directory exists on a different machine.

## 5. Validate tables, then decode images

```bash
.venv-ml/bin/python examples/04_inspect_dataset.py data/hub-so100-verified --expected-episodes 50
.venv-ml/bin/python examples/08_read_dataset.py \
  --root data/hub-so100-verified --repo-id lerobot/svla_so100_pickplace --index 20
```

The local check passed for 50 episodes and 19,631 frames. Both camera videos were decoded into `[3,480,640]` tensors and exported as PNGs under `outputs/`. That does not mean every demonstration was manually reviewed for task success.

LeRobot resolves shared episode/video files through metadata. Opening a table with general `datasets.load_dataset()` is not proof that synchronized robot video windows are being reconstructed correctly. [LeRobotDataset](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

## 6. Does selecting one episode mean a small download?

LeRobot supports selections such as `episodes=[0]`. In v3, many episodes can share one Parquet or MP4 shard. Access to one episode can therefore require a much larger shared file. Episode count is not a download-size estimate.

Streaming can avoid downloading an entire dataset in advance, but changes network, decoder and random-access behavior. Start with a small pinned local copy while learning to debug. Later compare the [official streaming workflow](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3#stream-datasets) against your installed version.

## 7. Prepare training

Record action dimensions, order, units, camera names and task first. Six action values do not prove the same physical meaning as six values on your arm. Do not arbitrarily rename `top`/`wrist`: dataset features and policy configuration must agree.

```bash
.venv-ml/bin/python examples/05_prepare_training.py \
  --root data/hub-so100-verified --repo-id lerobot/svla_so100_pickplace \
  --output-dir outputs/train/hub-so100-practice \
  --device cpu --steps 20 --batch-size 1
```

This only **generates** a training command. Executing that generated command can download model weights, and CPU training can be slow. See [compute setup](hesaplama.md) for fine-tuning. A model trained on this source dataset is not automatically ready to control your physical SO-101.

## 8. Prepare your own data for the Hub

Produce data locally, finalize it, validate tables and decode videos. Write a card containing robot type, task, action order/units, camera arrangement, FPS, expert source, success definition and license. [Data production](veri-uretimi.md) covers three routes.

Uploading is optional for training. When you choose to share, use your real user/organization namespace and intended visibility; `local/...` is an offline teaching identifier. After preparing account access and private/public settings, use the official `LeRobotDataset.push_to_hub` workflow. The workshop scripts do not upload data or create accounts. [Recording and Hub workflow](https://huggingface.co/docs/lerobot/en/il_robots)

**Deliverable:** a versioned local copy, clean numerical validation, decoded camera samples and a documented action/camera contract before training.
