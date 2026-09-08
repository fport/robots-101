# Troubleshooting

Find the smallest failing operation. Changing camera, CUDA, model and robot connection together makes the cause harder to isolate. Preserve the exact command and first meaningful error.

| Symptom | Likely layer | First check |
|---|---|---|
| `ModuleNotFoundError` | Python environment | Doctor output and interpreter path |
| Dependency cannot resolve | Python/version/platform | Python 3.12, published versions and intended requirements |
| `World already exists` | Strands initialization | Do not recreate a world after `Robot(...)` |
| SO-101 asset missing | Model download | First network error and cache permissions |
| Physics works, no PNG | OpenGL/rendering | Graphics session, supported backend and permissions |
| macOS viewer fails | Main thread | Use `mjpython ... --viewer` |
| Missing `observation.images.front` | Recording camera | Render that named camera before recording |
| One long episode instead of several | Episode boundaries | `save_episode` and actual metadata |
| `libtorchcodec` / `libavutil` | Video runtime | Torch/codec/FFmpeg compatibility; try PyAV |
| CUDA out of memory | Training memory | Reduce batch; inspect cameras and trainable layers |
| CUDA unavailable | Driver/wheel | `nvidia-smi` and appropriate PyTorch install |
| Missing model camera key | Input schema | Metadata, `input_features` and rename mapping |
| Numeric outputs, meaningless movement | Action contract | Units, order, statistics and gripper direction |
| Low loss, poor task success | Data/generalization | Coverage, independent tests and rollout failures |
| Busy port / sync read failure | Communication | Other process, power, cable and baud rate |
| MkDocs port occupied | Local server | Use another port or stop the old server |
| Hub download exceeds cap | Dataset size | Inspect full size, choose an intentional cap or metadata preview |
| Playground output already exists | Experiment preservation | Choose a new output directory |

## Failures observed in this workspace

System Python was 3.14; separate Python 3.12 environments avoided changing the system installation. Separating simulation and ML also kept incompatible NumPy/codec requirements apart.

The first SO-101 asset download encountered restricted network access; after downloading successfully, rendering worked. That failure was unrelated to motors or kinematics.

Restricted graphics access caused camera rendering to fail, which also left the recorder without its image observation. A render preflight was added before dataset creation. With graphics access, three episodes and 90 frames recorded successfully. Filling a missing camera with zeros would hide the failure.

TorchCodec could not load shared FFmpeg libraries. PyAV recording/reading worked, and the recipes explicitly select `dataset.video_backend=pyav`. TorchCodec was not verified as working on this machine.

The numeric one-hinge dataset stores its length-one action as a Parquet scalar. The inspector now accepts that storage form only for metadata shape `[1]`; a scalar still fails a declared six-action contract. The standard LeRobot reader also returns a scalar tensor for that single field, so custom teaching consumers should explicitly reshape it if they need a vector.

## Keep a useful log

```bash
mkdir -p outputs
.venv/bin/python examples/00_doctor.py > outputs/environment.json
```

For long training, capture stdout/stderr without credentials. Preserve the full trace and preceding command. After an out-of-memory failure, an existing notebook process may still hold model memory; a fresh small process helps separate that state from the intended experiment.

```text
Intended operation:
Exact command:
Expected output:
First error:
Python and package versions:
Operating system and GPU:
Robot port/calibration ID, if relevant:
Dataset feature summary:
Smallest reproduction:
```

For a data issue, share schema keys and a minimal episode/metadata reproduction instead of credentials or an entire large dataset. See [experiment design](../ogrenme/egitim-deneyleri.md) for hypotheses when code runs but behavior fails.
