# Worked questions

Write your answer before opening each solution. The aim is to recognize assumptions that lead to incorrect robotics conclusions. Use the [deeper reading route](../basla/derinlik.md) when you need background.

## 1. Six numbers, six independent pose coordinates?

The SO-101 action shape is `[6]`. Can you independently select x/y/z and roll/pitch/yaw?

??? success "Solution"
    No. One channel operates the gripper; the arm has five rotary joints. A general six-dimensional endpoint pose cannot be independently assigned. Reachability, limits and collisions also matter. Action dimension and task-space freedom are different concepts.

## 2. Radians or normalized values?

You send `0.5` in simulation. Will sending `0.5` with the hardware recipe's `use_degrees=false` produce the same angle?

??? success "Solution"
    Equal numbers do not establish equal angles. The inspected simulation uses radians; these hardware commands use calibrated normalized units. Order, zero, sign and ranges need mapping. Disabling degrees does not enable radians.

## 3. Physics and control clocks

Physics uses 0.002 s steps. How many substeps implement 50 Hz? What happens if you call `send_action(n_substeps=10)` and then `step(10)`?

??? success "Solution"
    A control period is 1/50=0.020 s, requiring ten substeps. The additional call advances ten more, totaling 0.040 s. Continuing to label each loop as 50 Hz misrepresents elapsed simulation time.

## 4. Target sent, target reached?

The reference equals the final target, but measured error is 0.08 rad with a 0.04 rad tolerance. Can the stage finish?

??? success "Solution"
    Not under the tracking contract. The servo must actually reach the target. Measured error must remain within tolerance for the required consecutive samples; reference equality alone is insufficient.

## 5. Two IK solutions

An 18/14 cm planar arm has two solutions for target `(22,10)` cm. Why not choose randomly?

??? success "Solution"
    The arm configurations differ despite the same endpoint. Distance from current pose, limits, table/body collisions and approach direction can favor one. Approximate solutions are `(−10.6301°,82.7046°)` and `(59.5180°,−82.7046°)`. This idealized arm is not SO-101 IK.

## 6. One pixel, two depths

Can camera-frame points `(0.05,0.02,0.50)` and `(0.10,0.04,1.00)` project to the same pixel?

??? success "Solution"
    Yes in the ideal pinhole model: X/Z and Y/Z are equal. One pixel defines a ray. A known camera matrix alone does not recover distance along that ray.

## 7. Camera matrix after resize and crop

For a 640×480 image, `fx=600`, `cx=320`. Halve the image, then crop 40 pixels from the left. What changes?

??? success "Solution"
    After resize, `fx=300` and `cx=160`. After the crop, `fx=300` and `cx=120`. The crop shifts the principal point; using the original matrix gives incorrect projections.

## 8. Which value is the label?

Current position is 0.10 rad, sent absolute target is 0.16 rad, next measurement is 0.12 rad. Give the absolute BC label, target delta and observed movement.

??? success "Solution"
    They are 0.16, 0.06 and 0.02 rad. Each defines a different learning problem. For an absolute-target `o_t → a_t` recipe the label is 0.16; substituting the next measured position changes the task.

## 9. Short episode, long chunk

Each starting frame in a 30-frame episode requests a 50-action window. What fraction is padding?

??? success "Solution"
    Valid slots total `30+29+...+1=465` out of `30×50=1500`. Padding is `1035/1500=69%`. Three equal-length episodes preserve that fraction. Targets must not cross episode boundaries, and padding must be masked in the objective.

## 10. Masked loss denominator

Squared errors at two valid steps are `[1,4]` and `[9,16]`; a third step is padding. After masking, should you divide by six elements?

??? success "Solution"
    No. Divide 30 by four valid elements to obtain 7.5. Dividing by six gives 5 and makes heavily padded batches look artificially better. `action_is_pad=true` marks an invalid time position.

## 11. Flow matching time

For `A=[0.2,−0.4]`, `ε=[1.0,0.6]`, `t=0.75`, calculate the interpolated sample and target field. Which direction does inference follow?

??? success "Solution"
    `x_t=(1−t)A+tε=[0.8,0.35]`; `u=ε−A=[0.8,1.0]`. In this implementation t=1 is noise and t=0 is data, so the Euler time increment is negative. This time is not the robot control clock.

## 12. Two step counts

With `num_steps=10`, `chunk_size=50` and 30 Hz control, what do these numbers describe?

??? success "Solution"
    Ten flow-solver updates produce one chunk. The chunk contains fifty robot commands, occupying about 1.67 seconds if all execute at 30 Hz. You cannot infer model latency as 10/30 seconds; measure it on the device.

## 13. Halving the batch

For 24,000 training frames, batch 8 and 20,000 updates, what is the approximate epoch equivalent? What if batch becomes 4?

??? success "Solution"
    Initially `160,000/24,000≈6.67`; afterward `80,000/24,000≈3.33`. Samplers and filters affect actual exposure. Equal update counts with different batches do not use equal numbers of samples.

## 14. Great validation, poor next-day performance

You split frames randomly 80/20. Validation is excellent but next-day task success is poor. What do you inspect first?

??? success "Solution"
    Inspect neighboring-frame/chunk leakage and changed image/starting conditions. Split whole episodes, and hold out days if your claim concerns new days. Check where normalization statistics came from. This observation alone does not establish a need for a larger model.

## 15. Improvement from 70% to 80%

Two checkpoints succeed 14/20 and 16/20 times. Is the second certainly better?

??? success "Solution"
    This small sample does not justify certainty. Report matched conditions, counts, failure types and uncertainty. Repeat a predefined evaluation. The observed improvement is useful evidence but does not establish broad generalization.

## 16. Why is mock data insufficient?

You produce 100 mock episodes with video, six action columns and valid timestamps. Why need SmolVLA not learn successful grasping?

??? success "Solution"
    Schema correctness does not supply behavioral expertise. If mock actions never demonstrate a successful grasping strategy, imitating them does not teach that task. First obtain suitable expert demonstrations and define an independent success test.

## Write a question about your own project

Choose one failed video and state an observation, two alternative hypotheses and one experiment that separates them. For example: the gripper closes in front of the object; camera latency or narrow training position coverage could explain it; compare timing traces at different motion speeds from a fixed start.

Reproduce at least four calculations in the terminal: IK, SO-101 target tracking, action windows and flow matching. Explain why the measured values agree or differ.
