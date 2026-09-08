# Robotics and learning glossary

Use this as a reference while reading. The Turkish pages introduce technical terms with their original English equivalents in parentheses.

| Term | Meaning |
|---|---|
| Action | Command sent at a control decision; meaning depends on the interface |
| Action chunk | Sequence of future actions |
| ACT | Action Chunking with Transformers, an imitation-learning policy |
| Actuator | Mechanism that applies motion or force |
| Asset | Model files such as meshes and MJCF |
| Batch | Group of samples processed together during an update |
| BC | Behavior cloning: learn expert actions from observations |
| Calibration | Relate measurements/targets to physical reference values |
| Checkpoint | Saved weights with relevant runtime or training state |
| Control frequency | Rate of control decisions or command execution |
| Controller | Rule or algorithm that produces control commands |
| CUDA | NVIDIA GPU computation platform |
| Dataset | Related observations, actions, tasks and metadata |
| Delta action | Change requested relative to a defined reference |
| Demonstration | Example behavior supplied by a teacher |
| DOF | Degree of freedom: an independent movement coordinate |
| Domain randomization | Controlled variation of visual/physical environment parameters |
| Embodiment | Robot body, sensing and action/state representation |
| End effector | Working tool at the arm's tip; here a gripper |
| Episode | One attempt with defined start and end |
| Epoch | Approximate pass through training samples |
| Fine-tuning | Adapt pretrained weights to a task or dataset |
| FK | Forward kinematics: joints to endpoint pose |
| Flow matching | Learn a vector field connecting noise and data distributions |
| Follower | Arm that physically performs the task |
| Frame | A time sample; may mean an image or full observation |
| Friction | Contact interaction resisting relative sliding |
| Gradient | Derivative showing how a change affects the objective |
| Gripper | Tool that holds an object between fingers |
| Headless | Without an interactive window; rendering may still need graphics |
| HIL | Human in the loop, supplying intervention or evaluation |
| IK | Inverse kinematics: endpoint target to joint values |
| Imitation learning | Learn behavior from demonstrations |
| Inference | Compute a prediction using fixed learned weights |
| Joint | Connection that permits defined motion between bodies |
| Leader | Human-operated arm used as a controller |
| Link | Rigid segment between joints |
| LoRA | Parameter-efficient adaptation using low-rank adapters |
| Loss | Numerical training objective measuring prediction error or fit |
| Metadata | Schema, counts, timing, task and file information |
| MJCF | MuJoCo's native XML model format |
| MPS | PyTorch's Apple GPU execution path |
| MuJoCo | Physics engine for articulated bodies and contact |
| Normalization | Statistical scaling of numerical features |
| Observation | Images, state and other inputs available at a decision |
| Optimizer | Algorithm that updates trainable model parameters |
| Overfitting | Fitting training examples without matching generalization |
| Padding | Extra entries preserving shape; mask invalid labels |
| Parquet | Column-oriented table storage format |
| Policy | Mapping from observations/tasks to actions |
| Pretraining | Broad learning before task-specific adaptation |
| Proprioception | Robot's measurements of its own state |
| qpos / qvel | MuJoCo generalized position and velocity state |
| Reset | Restore a specified initial episode state |
| Revision | Version identity, often a repository commit |
| RL | Reinforcement learning through reward-guided interaction |
| Rollout | Execute a policy over time in an environment |
| RTC | Real-time chunking, managing action-sequence timing/transitions |
| Seed | Random generator starting value; not full reproducibility by itself |
| Sim2real | Transfer simulated behavior to the physical system |
| SmolVLA | Compact vision-language-action model in the LeRobot ecosystem |
| State | Measured or simulated system-state vector |
| Teleoperation | Human control of a robot through another interface |
| Tensor | Multidimensional numeric array used by learning frameworks |
| Timestep | Simulation time advanced per physics update |
| URDF | Common XML robot geometry/joint description format |
| Validation | Reserved data used for model or setting selection |
| VLA | Vision–Language–Action, relating images, language and actions |
| VRAM | GPU memory |
| Waypoint | Intermediate target along a movement |

When a term describes a representation, also ask for units, reference, order and timing. Knowing the word “action” does not establish what six particular numbers command.
