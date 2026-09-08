---
hide:
  - toc
---

<div class="hero" markdown>
<div class="eyebrow">SO-101 WORKSHOP / START FROM ZERO</div>

# Meet your robot.<br>Before its first move.

<p class="intro">No robotics background required. Learn what a robot observes, how it moves, how to build a MuJoCo world and how demonstrations become a learned policy.</p>

<div class="hero-actions" markdown>
[I am completely new](basla/sifirdan.md){ .md-button .md-button--primary }
[Try the browser lab](temel/laboratuvar.md){ .md-button }
</div>

<p class="quiet">Reference: 8 September 2026 · Python 3.12 · Strands Robots 0.5.1 · LeRobot 0.6.1 · Türkçe / English</p>
</div>

<div class="route-grid" markdown>
<div class="route-card" markdown>
<span class="number">01 / UNDERSTAND</span>

### Learn the robot's vocabulary

Joints, gripper, observation, action and policy. Start with concrete examples before equations.

[Your first robotics session →](basla/sifirdan.md)
</div>
<div class="route-card" markdown>
<span class="number">02 / EXPERIMENT</span>

### Build a physics world

Drop a cube, change friction, track a target, produce camera images and load an SO-101.

[Simulation from scratch →](simulasyon/sifirdan.md)
</div>
<div class="route-card" markdown>
<span class="number">03 / TEACH</span>

### Turn demonstrations into behavior

Download a dataset, produce your own examples and train a small policy before moving to SmolVLA.

[Your first learning loop →](ogrenme/ilk-ogrenme.md)
</div>
</div>

## What will you build?

The eventual project is picking up an object and placing it in a defined tray. You first complete smaller tasks: joint tracking, camera placement and recording. Define success in advance, separate training from testing, and inspect failed attempts.

Two paths run alongside each other: practice with MuJoCo and Strands before delivery, then connect leader/follower teleoperation and real cameras when the arm arrives. Use a separate ML environment. Simulation can stay on your Mac while larger training runs on another NVIDIA machine.

!!! tip "Go deeper when you need it"
    [What should I know, and when?](basla/derinlik.md) connects skills to completion evidence. Work through IK, camera geometry, control, data engineering and SmolVLA internals, then try [16 worked questions](pratik/cozumlu-sorular.md).

## What runs here?

| Component | Result | Requirement |
|---|---|---|
| Browser lab | Kinematics, dataset size, action timing | Browser |
| `01_mujoco_basics.py` | One-joint physics tracking | Simulation environment |
| `02_strands_so101.py` | SO-101 asset, mock rollout, images | Initial asset download |
| `03_record_sim.py` | Separate image/action episodes | ML environment and graphics |
| `09_so101_waypoints.py` | Measured three-stage SO-101 tracking | Simulation environment |
| `13_mujoco_playground.py` | Five scene behaviors, ten experiments | MuJoCo; graphics for rendering |
| `14_hub_dataset.py` | Size-aware, pinned dataset download | ML environment and internet |
| `15_first_learning.py` | Generate, train, evaluate in physics | CPU ML environment |
| `16_create_lerobot_dataset.py` | Numeric CSV to real LeRobot format | ML environment |
| Physical SmolVLA rollout | Learned real-world task behavior | Robot, calibrated setup, data and checkpoint |

A mock rollout does not demonstrate learned grasping. The browser arm is a two-link mathematical exercise, not a MuJoCo digital twin. Full SmolVLA training and physical task success remain separate, unverified steps. Read the [validation record](basla/dogrulama.md).

## How to read

Start with the [beginner introduction](basla/sifirdan.md), then the [learning route](basla/rota.md). Every lab explains its purpose, command, expected result, variation and completion condition. Use [troubleshooting](pratik/sorunlar.md) to identify the failing layer. Technical sources are linked near their claims and in the [source register](kaynaklar.md).

This is an independent workshop, not Hashtag Robotics' official manual. The delivered kit's actual parts, power labels and supplier calibration instructions govern your hardware setup.
