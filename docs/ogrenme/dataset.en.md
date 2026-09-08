# Reading a LeRobot dataset

Robot training data link images, measured state, sent actions, task text and time indices. A folder of videos alone does not establish those relationships. For public downloads start with [Hugging Face datasets](huggingface.md); this page explains the local structure.

## Version 3 layout

LeRobot v3 stores numeric tables in Parquet, videos in MP4 shards and dataset information in metadata. One episode need not have its own video file; it can occupy an indexed interval in a shared file. Read the metadata instead of guessing filenames. [LeRobotDataset v3](https://huggingface.co/docs/lerobot/en/lerobot-dataset-v3)

```text
dataset-root/
  meta/
    info.json
    stats.json
    episodes/...
    tasks...
  data/
    chunk-.../file-....parquet
  videos/
    observation.images.front/...
    observation.images.wrist/...
```

This is a conceptual tree. Use the current `info.json` and episode metadata for exact paths. A v2.1 layout should not be manually imposed on v3 data.

| Field | Meaning |
|---|---|
| `episode_index` | Independent demonstration identity |
| `frame_index` | Position within that episode |
| `timestamp` | Sample time within that episode |
| `observation.state` | Measured state available at the decision |
| `action` | Target sent for that observation |
| `observation.images.front` | Image or associated video reference |
| Task index / text | Intended task |

Disk image metadata may be HWC while model batches use BCHW. The training command generator derives channel-first feature shapes from the metadata. Rearranging axes is different from converting BGR colors to RGB.

## Validate numeric rows

```bash
.venv-ml/bin/python examples/04_inspect_dataset.py data/sim-smoke-verified --expected-episodes 3
```

The script checks episode/frame order, timestamps against FPS, feature dimensions, finite values and metadata counts. The verified example has 3 episodes, 90 frames and `errors: []`. Length-one numeric features may be scalar in Parquet; the checker accepts that representation only when the declared shape is `[1]`.

This tool loads small workshop tables into memory. Large datasets need partitioned or streaming inspection. Passing it does not prove meaningful images, successful tasks or correct physical units.

## Decode a frame

```bash
.venv-ml/bin/python examples/08_read_dataset.py \
  --root data/sim-smoke-verified --repo-id local/sim-smoke
```

This opens a local root through `LeRobotDataset`, selects PyAV explicitly and writes camera PNGs. The tested Mac could not load TorchCodec's shared FFmpeg dependencies; PyAV decoding worked. Successfully encoding an MP4 does not establish that every decoder can load it.

## Normalization

Different numeric ranges often need scaling. A mean/standard-deviation example is:

```text
normalized = (raw - mean) / std
raw        = normalized * std + mean
```

The action postprocessor must use the matching statistics to undo the transform. Another dataset's statistics can have identical shapes and still produce incorrect targets. Constant channels, tiny standard deviations and clipping require the actual processor's behavior; avoid arbitrary manual patches.

## Training, validation and final test

Training updates weights. Validation helps choose checkpoints and settings. A final test reports performance on conditions that did not guide those choices. Splitting by episode reduces neighboring-frame leakage; it does not automatically test another day, camera arrangement or object.

The command generator uses `dataset.eval_split=0.2` for normal training and periodic evaluation loss. A three-episode smoke dataset is too small to yield a validation episode with this setting; use `--eval-split 0` only for a pipeline test. It does not create an independent final test.

For every version, record camera names/poses, robot/calibration IDs, action ordering and units, FPS, task text, success definition, demonstration source and split policy. Resolve mismatches between this contract and the model input before training.
