# Teleoperation and cameras

Teleoperation means a human operates the robot through another controller. Here you move the leader arm and the follower receives corresponding targets. It gives you a practical way to collect demonstrations before a learned policy exists.

Complete [first power-on](ilk-acilis.md) and keep its port and ID variables in the current terminal. This command moves physical hardware:

```bash
lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port="$FOLLOWER_PORT" \
  --robot.id="$FOLLOWER_ID" \
  --robot.use_degrees=false \
  --robot.max_relative_target=2 \
  --teleop.type=so101_leader \
  --teleop.port="$LEADER_PORT" \
  --teleop.id="$LEADER_ID" \
  --teleop.use_degrees=false \
  --fps=30
```

The value `max_relative_target=2` limits the relative target in the selected normalized units per update. It is not two degrees, a calibrated speed limit, or a guarantee against contact. Begin with small leader movements and observe the follower. [LeRobot teleoperation](https://huggingface.co/docs/lerobot/en/il_robots#teleoperate)

## Find the cameras

```bash
lerobot-find-cameras opencv
```

Choose the actual indices from its output. The following `0` and `1` are examples:

```bash
export CAMERAS='{front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 1, width: 640, height: 480, fps: 30}}'
```

If you own one camera, remove the other entry. Do not declare a camera that is absent. `front` and `wrist` are feature names: preserve them from recording through training and deployment. A different name in the pretrained model needs an explicit feature configuration, as explained in [SmolVLA training](../ogrenme/smolvla.md).

Add `--robot.cameras="$CAMERAS"` to the teleoperation command to connect the configured cameras. Optional visualization uses `--display_data=true` and may require the visualization extra:

```bash
uv pip install --python .venv-ml/bin/python 'lerobot[viz]==0.6.1'
```

First inspect the camera views without trying to complete a fast task. Put the object at five intended starting positions. Can you see the object, both gripper fingers, the lift and the destination? Keep focus and mounting stable. Two USB cameras can share bandwidth; test their real capture rates together. A printed 30 FPS specification does not establish synchronization.

The front view gives workspace context; the wrist view can help around contact but changes with arm motion. Learn their geometry in [camera calibration](kamera-kalibrasyonu.md). An image-free dataset can teach numeric control, but it does not supply visual input for the SmolVLA recipe here.

## If you only have a follower

A leader is one demonstration device, not a mathematical requirement. A keyboard, gamepad, joint interface or Cartesian controller needs its own mapping, limits and feedback. Cartesian commands additionally need inverse kinematics. Start with a tested control path; do not assume a language model automatically provides a usable demonstration controller.

Strands also exposes hardware and teleoperation interfaces. Introduce them after the standard LeRobot path works, with one process owning the device. This workspace verified Strands in simulation only. Continue with [collecting useful data](veri.md).
