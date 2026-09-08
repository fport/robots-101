# GPU and cloud workflow

You can keep a Mac next to the robot and train on another computer. Separating recording and training machines does not require network control of the physical arm: move data out and bring the trained checkpoint back.

| Work | Mac / CPU | NVIDIA CUDA machine |
|---|---|---|
| MkDocs and small Python exercises | Suitable; tested locally | Not required |
| One SO-101 MuJoCo environment | Tested locally | Also possible |
| Camera recording | Depends on USB and codecs | Also possible |
| Small NumPy/PyTorch teaching models | Tested on CPU | Not required |
| SmolVLA fine-tuning | CPU is slow; MPS needs validation | Main training recipe |
| Real-time VLA | Measure latency and memory | Still model/device dependent |

VRAM depends on batch, cameras, resolution, precision, trainable layers and optimizer. Begin with batch 1 and measure before increasing it. Parameter count alone does not determine training memory. [LeRobot hardware guide](https://huggingface.co/docs/lerobot/en/hardware_guide)

## CUDA setup order

On Linux, install the driver using the provider/distribution instructions and verify `nvidia-smi`. Select a compatible PyTorch wheel using the [official installer](https://pytorch.org/get-started/locally/); do not guess a CUDA package index.

```bash
uv venv --python 3.12 .venv-ml
uv pip install --python .venv-ml/bin/python -r requirements-ml.txt
source .venv-ml/bin/activate
python examples/00_doctor.py
python -c 'import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No CUDA")'
```

If CUDA is unavailable, resolve driver, wheel or device visibility before training. A GPU visible on the host may not be exposed inside a container. Mac uses CPU/MPS rather than CUDA.

## Video runtime dependencies

TorchCodec needs compatible PyTorch and shared FFmpeg libraries. Having an `ffmpeg` executable does not prove the dynamic loader can find libraries such as `libavutil`. [TorchCodec compatibility and installation](https://github.com/pytorch/torchcodec#installing-torchcodec)

On the tested Mac, TorchCodec could not load its shared dependencies; PyAV reading worked. The workshop training recipe selects PyAV explicitly. To adopt TorchCodec later, install compatible FFmpeg libraries through your system package manager and verify a short decode before changing the full pipeline.

## Transfer the complete dataset

1. Finish recording and run integrity checks on the robot machine.
2. Transfer the root with `meta`, `data` and `videos` together.
3. Repeat inspection and frame decoding on the training machine.
4. Regenerate the training command with that machine's paths.
5. Retrieve checkpoints, commands, package versions and evaluation notes.

Example for an existing SSH-accessible server; replace the placeholders:

```bash
rsync -av --progress data/so101-pick-v1/ USER@GPU_HOST:/workspace/data/so101-pick-v1/
```

This does not provision a GPU server. Keep credentials out of repository files.

## Budget a cloud session from measurements

Start with environment setup, data reading and a 100-update smoke run. Estimate after observing steady step time:

```text
remaining training time ≈ remaining updates × steady seconds/update
total session ≈ setup + download + training + evaluation + result transfer
```

Cost depends on the provider's current compute, storage and network pricing; no fixed price is assumed here. Closing a notebook tab may leave the GPU instance running. Check the provider's actual job state and preserve results on durable storage.

Choose checkpoint frequency based on the amount of work you can lose to interruption. Writing every update adds I/O; never saving risks the whole run. Test resume before a long interruptible job.

## Multiple GPUs

First establish a working single-device pipeline with useful data. Multiple devices change communication overhead, effective batch and reproducibility. Distributed training is a later optimization exercise, outside these single-device commands. [LeRobot multi-GPU guide](https://huggingface.co/docs/lerobot/en/multi_gpu_training)
