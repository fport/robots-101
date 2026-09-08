# Your learning route

Before delivery, build [your first physics world](../simulasyon/sifirdan.md), try [ten experiments](../simulasyon/deneyler.md) and complete [the first learning loop](../ogrenme/ilk-ogrenme.md). Practice with [Hub downloads](../ogrenme/huggingface.md) and [your own data](../ogrenme/veri-uretimi.md). These additions are labs 17–22 in the practice notebook.

If you are entirely new, begin with [the introductory chapter](sifirdan.md). The first twelve milestones establish the overall workflow. Additional labs explore IK, measured control, data windows, flow matching, the MuJoCo playground and a complete small learning loop. The checklist is a starting-route tracker, not an expertise score.

The goal is to identify whether a failure belongs to physics, communication, data or learning. Suggested stages are not delivery or training-time promises.

## Four stages

| Stage | Work | Evidence |
|---|---|---|
| Before delivery | Setup, units, MuJoCo, SO-101 scene | Your own image, state report and tracking CSV |
| Data pipeline | Episodes, action/state, recording, validation | Actual separate episodes that pass inspection |
| After delivery | Mounting, ports, calibration, teleop, cameras | Controlled movement and five pilot demonstrations |
| Learning loop | Better data, ACT/SmolVLA, evaluation | Measured performance on held-out tasks |

Keep a short experiment note: date, package versions, one changed variable, observed result and next question. Include experiment IDs in filenames, such as `run-004_camera-front_ep-003.mp4`.

## Local progress notebook

Checks are stored in this browser and shared between the two language editions on the same origin. There is no server account or cloud synchronization. Clearing browser data removes them.

<div class="progress-list lab-panel" id="learning-progress">
<p id="progress-summary" aria-live="polite"></p>
<progress max="12" value="0" aria-label="Learning progress"></progress>
<label><input type="checkbox" id="p01">01 — I identified the Python environments and read the doctor report.</label>
<label><input type="checkbox" id="p02">02 — I can explain degrees/radians and joints/tip position.</label>
<label><input type="checkbox" id="p03">03 — I ran the MuJoCo hinge experiment.</label>
<label><input type="checkbox" id="p04">04 — I generated an SO-101 image with Strands.</label>
<label><input type="checkbox" id="p05">05 — I recorded three episodes and checked their counts.</label>
<label><input type="checkbox" id="p06">06 — I mounted the hardware and verified its power/calibration information.</label>
<label><input type="checkbox" id="p07">07 — I performed controlled leader teleop and checked both cameras.</label>
<label><input type="checkbox" id="p08">08 — I watched five pilot demonstrations and fixed problems.</label>
<label><input type="checkbox" id="p09">09 — I completed a data plan and separated test conditions.</label>
<label><input type="checkbox" id="p10">10 — I completed a short ACT or SmolVLA training run.</label>
<label><input type="checkbox" id="p11">11 — I recorded outcomes and failure causes in separate evaluations.</label>
<label><input type="checkbox" id="p12">12 — I compared a data improvement using a new checkpoint.</label>
<button type="button">Reset checks</button>
</div>

## Leader and compute choices

**Leader and follower:** leader teleoperation is the direct route to physical demonstrations. Reading the leader supplies follower targets; no learned model is needed initially.

**Follower only:** all simulation and downloaded-data exercises remain available. Physical demonstrations require a compatible controller, keyboard/gamepad with kinematic mapping, or a leader later. `x += 1` is not a motor target: IK, limits and rate management are required. Do not force a torque-enabled arm by hand.

**Mac only:** begin with CPU simulation and data inspection. Apple Silicon MPS may support particular learning/inference workloads; verify operator, package and memory compatibility with small runs. You can use a separate NVIDIA machine later. A working small data pipeline is the first objective.

## Completion evidence

Report all predefined attempts with checkpoint identity and failure categories. For example, “same lighting, five starting regions, four repeats, 14/20 successful” describes a useful workshop test. It does not establish performance on untested objects. See the [depth roadmap](derinlik.md) and [capstone](../pratik/proje.md).
