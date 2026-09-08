# Generate and record demonstrations

Simulation lets you learn the recording/training pipeline while waiting for hardware. The behavior you can learn depends on the teacher: random motion, a verified scripted expert and a human demonstration are different sources.

| Source | Use | Limit |
|---|---|---|
| Mock/random | Schema, video and episode pipeline checks | Does not teach successful task behavior |
| Scripted/IK expert | Controlled demonstrations for a defined task | Contact and success must be verified |
| Human teleoperation | Examples of task-solving behavior | Operator and recording quality matter |

Start with mock to test infrastructure, then use a reliable expert or suitable downloaded data. Attractive motion is not sufficient evidence of expertise.

## Working recorder

```bash
.venv-ml/bin/python examples/03_record_sim.py
.venv-ml/bin/python examples/04_inspect_dataset.py data/sim-smoke --expected-episodes 3
```

Defaults are three episodes with 30 control steps each: 90 records, front camera 256×256, recording/control rate 30. Existing output roots are refused. For a new experiment:

```bash
.venv-ml/bin/python examples/03_record_sim.py --root data/sim-smoke-02 --episodes 4 --steps 60
```

`ATOLYE_README.json` identifies this as mock pipeline data, not a grasp-success dataset.

## Episode boundaries

Concatenating three attempts and only saving at the end can create one long episode. A reset jump could then appear as part of a demonstrated action sequence. This script calls `save_episode()` after each rollout and `stop_recording()` at the end. Validate actual records, not a printed attempt counter. [Strands recording](https://github.com/strands-labs/robots/blob/main/docs/recording.md)

## Recording FPS and physics time

Both recording FPS and control frequency are set to 30. That is a necessary initial contract, but physics substep rounding still needs checking. The tested 30-step SO-101 rollout reported about **1.02 simulated seconds**, because 30 Hz does not divide a 0.002 s timestep exactly. Do not equate the metadata's 30 FPS with exactly 1.000 seconds of evolved physics. The [50 Hz tracking exercise](denetleyici.md) avoids this ratio mismatch.

## Validate images too

Parquet inspection does not decode all video frames. Check camera keys/files and watch an episode end to end. Frozen, wrong or delayed images can exist inside a numerically valid dataset. Fix encoder problems with three short episodes before recording hours of data.

## Improve simulation data for learning

Begin with one object, one target region and limited start variation. Run a verified expert over multiple seeds and keep success/failure labels distinct. Train an initial BC baseline on suitable successful demonstrations and evaluate unseen starts.

Then vary lighting, color, object position or friction separately. An image augmentation should preserve label validity: moving the depicted object while retaining unrelated actions can create an invalid pair.

Read [data production](../ogrenme/veri-uretimi.md), [Hub datasets](../ogrenme/huggingface.md) and [SmolVLA training](../ogrenme/smolvla.md). A technical training run on mock data does not establish task performance.
