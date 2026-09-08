# Combining the system with a Strands agent

A language-model agent can inspect tools and coordinate high-level tasks. A VLA predicts robot actions from observations. A low-level controller applies commands at a defined rate. These roles have different timing and responsibilities.

## Start with a direct simulator call

```python
from strands_robots import Robot

robot = Robot("so101", mode="sim", mesh=False)
try:
    print(robot.get_robot_state("so101"))
finally:
    robot.cleanup()
```

Direct Python calls do not need an LLM account. For reproducible recording, explicit Python loops make observation/action timing easier to inspect. The full setup is in [Strands simulation](../simulasyon/strands.md).

## Add a read-only agent task

The installed integration exposes the robot as a collection of tools. This example requires a configured model provider:

```python
from strands import Agent
from strands_robots import Robot

robot = Robot("so101", mode="sim", mesh=False)
try:
    agent = Agent(tools=[robot])
    agent("Read and explain the current SO-101 state. Do not recreate the world or move the robot.")
finally:
    robot.cleanup()
```

The default Strands agent provider uses Amazon Bedrock and requires its account, credentials and model access. Other providers have their own configuration. This agent example was not executed against a paid provider in this workspace. [Strands model providers](https://strandsagents.com/docs/user-guide/concepts/model-providers/)

## Useful first agent exercises

- Read and explain the existing simulation state.
- List available cameras and request a view.
- Summarize a completed experiment's metrics.
- Choose among predefined simulation experiments with explicit parameters.

Add one capability at a time and inspect tool results. A fluent explanation is not proof that a tool succeeded; code should check structured status and errors. Do not put a conversational model in charge of millisecond servo timing.

For physical hardware, begin with read-only inspection and one process owning the device. Any later task runner needs bounded duration, known commands, timeout handling and clear failure behavior implemented in the application. A language instruction by itself does not implement those controls. [Strands Robots source](https://github.com/strands-labs/robots)
