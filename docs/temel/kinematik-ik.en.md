# Kinematics, inverse kinematics and singularities

You will solve a target in two ways, verify both using forward kinematics and explain why a mathematical solution might be invalid on a real arm. First read [coordinates and control](robotik.md).

Our teaching arm has two planar links of **18 cm and 14 cm**. These are not SO-101 link dimensions or its IK model.

## 1. Forward kinematics

q1 is the first link's angle relative to x. q2 is the second link's angle **relative to the first**, so its world angle is q1+q2.

```text
x = L1 cos(q1) + L2 cos(q1 + q2)
y = L1 sin(q1) + L2 sin(q1 + q2)
```

For q1=0 and q2=π/2, the first link points 18 cm right and the second 14 cm up: tip `(0.18,0.14)` m. Using q2 alone for the second world angle fails when the first link rotates.

Python trigonometric functions use radians. `90°=π/2 rad`; `np.sin(90)` is not the sine of 90 degrees. Convert at input/output boundaries.

## 2. Is the target reachable?

Without limits or obstacles, distance r from the base satisfies:

```text
r = sqrt(x² + y²)
abs(L1 - L2) <= r <= L1 + L2
0.04 m <= r <= 0.32 m
```

Fully extending reaches 32 cm; fully folding leaves 4 cm. More IK iterations cannot reach `(0.40,0)` m. Physical limits, the body and the table further restrict the ideal region.

## 3. Worked IK: target (22 cm, 10 cm)

The cosine rule gives:

```text
c2 = (x² + y² - L1² - L2²) / (2 L1 L2)
   = (0.22² + 0.10² - 0.18² - 0.14²) / (2 × 0.18 × 0.14)
   ≈ 0.126984
q2 = ±acos(c2)
q1 = atan2(y,x) - atan2(L2 sin(q2), L1 + L2 cos(q2))
```

| Branch | q1 | q2 | Reconstructed tip |
|---|---|---|---|
| A | −10.6301° | +82.7046° | `(0.22,0.10)` m |
| B | +59.5180° | −82.7046° | `(0.22,0.10)` m |

Elbow-up/down names depend on your axes; recording signs is unambiguous. `atan2` preserves quadrant information that `atan(y/x)` alone loses.

```bash
.venv/bin/python examples/12_planar_ik.py
.venv/bin/python examples/12_planar_ik.py --x 0.18 --y 0.14
.venv/bin/python examples/12_planar_ik.py --x 0.40 --y 0
```

The final command should fail. The script checks FK round trips with numerical tolerance `1e-12 m`; this is calculation consistency, not real arm accuracy.

## 4. Choose a branch

Jumping from a configuration near A to B can request a large motion. Check limits, continuity, collision and approach direction. The same tip point does not imply the same occupied volume.

A practical scheme rejects invalid branches and compares the remaining weighted joint distances to current state. Angular wrapping matters: 179° and −179° are not always separated by a physically relevant 358°, while hard joint limits may prevent wraparound.

SO-101 requires its actual joint axes, link transforms, limits and gripper geometry. Adding four columns to this planar equation does not create its model.

## 5. Transform coordinates

Define `T_base_camera` to map camera-frame points into base coordinates:

```text
p_base = R_base_camera p_camera + t_base_camera
T = [ R(3×3) t(3×1) ]
    [ 0 0 0     1    ]
```

For aligned axes and camera origin `(0.10,0,0.30)` m in the base, camera point `(0.02,0.03,0.40)` becomes `(0.12,0.03,0.70)` m. This is arithmetic, not the expected orientation of a real downward-looking camera.

The inverse is `Rᵀ` and `−Rᵀt`, not merely changing the sign of translation. In a chain, frame names must cancel: `T_base_camera T_camera_object = T_base_object`. Knowing camera pose does not supply object depth. See [camera calibration](../donanim/kamera-kalibrasyonu.md).

## 6. Jacobian: the effect of a small movement

For small changes, `Δp ≈ J(q)Δq`:

```text
J = [ -L1 sin(q1)-L2 sin(q1+q2)  -L2 sin(q1+q2) ]
    [  L1 cos(q1)+L2 cos(q1+q2)   L2 cos(q1+q2) ]
```

At branch A:

```text
J ≈ [ -0.100000  -0.133204 ] meters/radian
    [  0.220000   0.043089 ]
```

`Δq=(0.01,0)` rad approximately moves the tip `(-0.001,0.0022)` m. Larger changes require recalculation because this is a local linear approximation. The script also verifies the analytical Jacobian using central finite differences: perturb each joint by ±ε and divide the FK difference by 2ε.

## 7. Why singularities matter

At q2=0, `det(J)=L1 L2 sin(q2)=0`. Some instantaneous tip directions cannot be produced to first order, and a small requested tip change can lead to a large joint correction.

Numerical IK iteratively maps tip error into joint corrections. A pseudoinverse handles non-square/singular matrices; the initial guess affects convergence. [Modern Robotics numerical IK](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/)

A damped least-squares update follows:

```text
min_Δq ||J Δq - e||² + λ² ||Δq||²
Δq = Jᵀ (J Jᵀ + λ² I)⁻¹ e
```

The first term reduces tip error; the second discourages large joint changes. Larger damping makes updates more conservative and is sensitive to units. Solve the linear system rather than explicitly constructing an inverse. Damping does not make unreachable targets reachable or replace limit/collision checks.

## 8. Why learn IK if using VLA?

A joint-action VLA need not call your analytical IK at every step. Geometry still matters when creating demonstrations, defining task boundaries and inspecting failures. If a policy reaches below the table, distinguish a frame error, unreachable goal and wrong action unit.

**Exercise:** run `--x 0.32 --y 0`. Explain branch merging and the smallest singular value approaching zero, then move the target 1 cm farther and predict the rejection.
