# First power-on and calibration

Read this when the physical kit arrives. The simulator does not verify your wiring, power supply, motor IDs or calibration. Mount the base firmly, clear the workspace, route cables away from joints and keep the power disconnect within reach. Check the supply specification against the actual kit and motor variant before connecting it.

## An assembled kit is different from loose motors

The linked Hashtag Robotics kit is described as an assembled leader/follower set. Ask which motor setup and calibration steps the supplier has already completed. Do not overwrite working factory IDs as a routine first step. Motor setup assigns communication IDs; calibration records joint ranges and reference positions. They are separate operations. For an unconfigured motor kit, follow the official sequence, including connecting individual motors when instructed. [SO-101 setup](https://huggingface.co/docs/lerobot/en/so101), [supplier page](https://labs.hashtagrobotics.tr/so-101-robot-kol)

## Identify the ports

From the project directory:

```bash
source .venv-ml/bin/activate
python examples/00_doctor.py
lerobot-find-port
```

Follow the port tool's disconnect/reconnect instructions. Replace these placeholders with the actual ports; they are not usable device names:

```bash
export FOLLOWER_PORT='/dev/tty.usbmodem_WRITE_REAL_FOLLOWER_PORT'
export LEADER_PORT='/dev/tty.usbmodem_WRITE_REAL_LEADER_PORT'
export FOLLOWER_ID='atolye_follower'
export LEADER_ID='atolye_leader'
```

Linux names may look like `/dev/ttyACM0`; use the detected value. The ID strings select persistent calibration identities. Keep the same IDs in calibration, teleoperation, recording and rollout commands.

## Choose the units explicitly

These hardware recipes use `use_degrees=false` on both arms. In this mode arm joints use calibrated normalized values in `[-100,100]`, and the gripper uses `[0,100]`. These are not radians. Installed LeRobot 0.6.1 defaults to degrees, so leaving the flag out changes the contract. MuJoCo examples use radians; do not copy their targets directly into this hardware interface.

Preserve valid supplier calibration when available. If calibration is needed, run the appropriate commands and follow their terminal instructions:

```bash
lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false

lerobot-calibrate \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.use_degrees=false
```

Move only as the calibration procedure asks. Do not force mechanical stops. Preserve the calibration files and record which physical arm each ID belongs to. Reusing an unrelated arm's calibration because its connector fits is not a valid shortcut.

## First movement

Start with small, slow teleoperation movements in free space. Check each joint's direction and gripper opening. A large unexpected motion is a reason to stop and check the port, calibration, units and mapping. Use one process on the motor bus; a recorder, teleoperation process and separate hardware agent should not compete for the same port.

| Symptom | First checks |
|---|---|
| No serial device | USB cable with data support, connector and OS permissions |
| Port exists but motors do not answer | Correct power, selected port and motor IDs |
| Joint motion is reversed or offset | Matching physical arm, calibration identity and units |
| Port busy | Another process still owns it |
| Calibration cannot complete | Correct setup order and mechanical range; inspect the official procedure |

These hardware commands are documented recipes, not physical tests performed in this workspace. Continue with [teleoperation and cameras](teleop.md).
