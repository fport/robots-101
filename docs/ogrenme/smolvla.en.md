# Fine-tuning SmolVLA

This is the command recipe. Read [the first learning experiment](ilk-ogrenme.md) before it if training is new, then [SmolVLA internals](smolvla-ic-yapi.md) for tensors, flow matching and the optimizer. Full SmolVLA weights and GPU training were not run in this workspace; command generation and installed configuration parsing were verified.

## Prepare the actual input contract

Use the [ML environment](../basla/kurulum.md) and inspect the dataset. The base model's camera names may be `camera1`, `camera2`, `camera3`, while your data have `front` and `wrist`. The generator reads actual metadata to configure existing camera features and sets `empty_cameras=0`. It requires six state/action dimensions and at least one image feature.

Disk `[480,640,3]` becomes a policy feature `[3,480,640]`; batched images add the batch axis. Matching dimensions is a necessary check, not proof of matching robot units or camera viewpoints.

```bash
source .venv-ml/bin/activate
python examples/00_doctor.py
python examples/04_inspect_dataset.py data/so101-pick-v1
```

## Generate a short training command

```bash
python examples/05_prepare_training.py \
  --root data/so101-pick-v1 \
  --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/smolvla-smoke \
  --steps 100 --batch-size 1 --device cuda --eval-split 0 \
  --save-command outputs/commands/smolvla-smoke.sh
```

This only prints and saves a command. Read the saved file. Running the following starts model download and training on the selected device:

```bash
bash outputs/commands/smolvla-smoke.sh
```

`cuda` requires a compatible NVIDIA environment. On a Mac choose CPU or MPS deliberately and validate support and memory; full SmolVLA execution on MPS was not verified here. The 100-step run tests data loading, forward/backward and saving, not task quality. `eval-split=0` disables held-out evaluation for this smoke run.

## Generate the main experiment

After confirming useful demonstrations and enough episodes for validation:

```bash
python examples/05_prepare_training.py \
  --root data/so101-pick-v1 \
  --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/smolvla-pick-v1 \
  --steps 20000 --batch-size 8 --device cuda --eval-split 0.2 \
  --save-command outputs/commands/smolvla-pick-v1.sh

bash outputs/commands/smolvla-pick-v1.sh
```

20,000 updates and batch 8 are a starting experiment, not measured optimal settings. Use a fresh output directory for each run. The generator rejects splits that leave no validation episode. Three smoke episodes are insufficient for its default 0.2 split.

| Generated setting | Purpose |
|---|---|
| `policy.path=lerobot/smolvla_base` | Load the pretrained starting policy |
| `policy.input_features` | Match the real state and camera schema |
| `policy.empty_cameras=0` | Avoid inventing missing cameras |
| `policy.train_expert_only=true` | Adapt the action side with the VLM frozen |
| `policy.freeze_vision_encoder=true` | Keep the visual encoder frozen |
| `policy.train_state_proj=true` | Train state projection |
| `dataset.video_backend=pyav` | Use the tested local decoder path |
| `num_workers=0` | Start with simple loading; tune after measuring |
| `policy.push_to_hub=false`, `wandb.enable=false` | Keep these uploads/log integrations disabled |
| `seed=42` | Record a reproducible random seed |

The actual checkpoint config remains authoritative. This is expert fine-tuning, not automatic LoRA or pretraining from scratch. Inspect trainable parameters as shown in [internals](smolvla-ic-yapi.md). [Official SmolVLA guide](https://huggingface.co/docs/lerobot/en/smolvla)

## What to inspect while it runs

Confirm the dataset, feature names, selected device and trainable parameters. Loss should remain finite. Separate download/startup time from steady step time. Record learning rate, memory, throughput and validation behavior. A falling training loss needs subsequent task evaluation; it cannot prove a successful grasp.

Generated paths are resolved for the current machine. If you transfer data to another host, regenerate the command there. Preserve the full command and package versions with the experiment card.

## Checkpoints and resume

A typical final policy directory is:

```text
outputs/train/smolvla-pick-v1/checkpoints/last/pretrained_model/
```

Inspect the actual saved tree. Runtime needs configuration and preprocessing files as well as weights. Resuming optimization also requires the full training state, including optimizer and RNG state; a standalone inference export is not equivalent.

```bash
lerobot-train \
  --config_path=outputs/train/smolvla-pick-v1/checkpoints/last/pretrained_model/train_config.json \
  --resume=true
```

Test resume on a short run before depending on it for a long cloud job. Use the path your run actually produced.

## ACT comparison on the same data

```bash
python examples/05_prepare_training.py \
  --policy act --root data/so101-pick-v1 --repo-id local/so101-pick-v1 \
  --output-dir outputs/train/act-pick-v1 \
  --steps 20000 --batch-size 8 --device cuda --eval-split 0.2 \
  --save-command outputs/commands/act-pick-v1.sh
```

This also only generates a command. Keep dataset splits and task tests comparable. Different loss functions cannot be compared as if their numerical values were the same metric. Continue with [experiment design](egitim-deneyleri.md) and [evaluation](degerlendirme.md).
