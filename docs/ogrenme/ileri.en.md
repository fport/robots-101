# Advanced work and reinforcement learning

After measuring an end-to-end task, choose the next method according to the bottleneck. Every method still depends on matching camera, action, timing and success contracts.

## Asynchronous inference and RTC

Executing an earlier action chunk while computing the next can hide some latency. It also raises questions: how old is the new chunk's observation, which queued actions have already executed, and how should trajectories join? Measure p50/p95 latency and queue starvation before changing scheduling.

RTC addresses chunk transition and timing issues. An invented `async=true` flag is not an implementation; follow the supported inference configuration for your version. [Asynchronous inference](https://huggingface.co/docs/lerobot/en/async), [RTC](https://huggingface.co/docs/lerobot/en/rtc)

## LoRA and PEFT

Adapter-based methods update a smaller set of parameters, potentially reducing training memory. Policy support, target modules and checkpoint export behavior still matter. This workshop's SmolVLA recipe fine-tunes the action expert; it is not a LoRA recipe. Compare trainable parameter counts, measured memory and task outcomes if you investigate adapters. [LeRobot PEFT](https://huggingface.co/docs/lerobot/en/peft_training)

## Human intervention

A human can take over after a policy makes a small mistake and demonstrate recovery from a state the policy actually visits. Record intervention boundaries, action source and episode labels. DAgger relates to this distribution problem: it still requires a suitable teacher target, rather than adding arbitrary failed actions to a successful dataset. [Human-in-the-loop collection](https://huggingface.co/docs/lerobot/en/hil_data_collection)

## Reinforcement learning

RL learns from rewards through interaction, optionally alongside demonstrations. An environment specifies observations, actions, rewards, termination and truncation. MuJoCo supplies physics; it does not automatically define a complete RL task.

A first project can be reaching a target. Observe joint state and target position, use bounded target changes as actions, and define distance and success rewards. A distance-only reward can ignore table or obstacle violations, so evaluate constraints as well as progress. Reward shaping, reset distribution and termination directly influence learned behavior.

Reserve new initial conditions for testing. Thousands of simulation steps still cost computation; parallel environments require seed and version management. [LeRobot simulation RL](https://huggingface.co/docs/lerobot/en/hilserl_sim)

| Bottleneck | Next experiment |
|---|---|
| Visual changes cause errors | Controlled lighting/background variation with held-out tests |
| Small errors cannot be recovered | Correctly labeled recovery demonstrations |
| Inference misses control deadlines | Latency profiling, execution horizon and RTC |
| GPU waits for data | Profile decoder, workers and prefetch |
| One camera becomes occluded | Add another view and retrain with matching data |
| RL exploits an unwanted shortcut | Revisit reward, success and reset definitions |

ROS 2 can help integrate existing robot nodes and sensors. Other GPU simulators can be explored for large-scale rendering or parallel training. They are not prerequisites for the first SO-101 loop. Use a separate environment when a concrete need appears.

Even for simulation-only success, record the environment, embodiment, camera and action space. Truncating another robot's checkpoint output to six numbers is not a validated transfer method.
