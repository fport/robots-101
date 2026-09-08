# Camera geometry and calibration

Visual learning does not make camera errors disappear automatically. You need a reproducible arrangement and correct timing/visibility. Explicit geometry becomes especially useful for localization or matching simulated and real cameras.

## 1. Four different calibration jobs

| Job | Relationship | Output |
|---|---|---|
| Servo calibration | Motor readings and joint references/range | Offsets and limits |
| Camera intrinsics | Camera rays and pixels | K and distortion |
| Camera extrinsics | Camera and robot/table frames | R,t or T |
| Learning normalization | Dataset values and model scale | Mean/std and transforms |

A camera matrix does not prove motor directions. Normalization does not transform camera coordinates into robot coordinates.

## 2. Project a point

For camera-frame `(X,Y,Z)` with Z>0 in the ideal pinhole model:

```text
u = fx X/Z + cx
v = fy Y/Z + cy
K = [ fx  0 cx ]
    [  0 fy cy ]
    [  0  0  1 ]
```

fx/fy are pixel focal parameters, cx/cy the principal point. Lens distortion is modeled separately. Calibration estimates these from known pattern points and image observations. [OpenCV camera model](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html)

With fx=fy=600, cx=320, cy=240 and point `(0.05,-0.02,0.50)` m, the pixel is `(380,216)`. Point `(0.10,-0.04,1.00)` lies on the same ray and produces the same pixel. A single RGB pixel cannot determine which depth is correct. You need extra geometry, a known plane/scale, multiple views or a depth sensor.

## 3. Camera and robot axes

OpenCV's common camera convention is x right, y down and z forward. Robot base and MuJoCo viewing conventions can differ. Identical axis labels do not establish a correct transform. Verify a known point numerically in each frame. [Projection/extrinsics reference](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html)

Read the direction of `solvePnP` results: an object-to-camera transform is not automatically camera-to-base. Use explicit names such as `T_base_camera`. Project a known base point back into the image and compare with the actual image before trusting the chain.

## 4. Collect intrinsic calibration observations

For a pattern with 9×6 **inner corners** and 20 mm squares, measure the printed dimensions. Nine-by-six squares is a different pattern. Mount it flat; a warped sheet violates the assumed geometry.

As a starting exercise, collect 15–25 varied views, not a universal sufficiency threshold. Include image edges, different tilts and distances. Twenty near-identical images do not add geometric diversity. Check blur and focus changes.

The OpenCV flow detects corners, refines them to subpixel positions, matches them to known pattern points and calls `calibrateCamera`. Evaluate reprojection afterward. [Calibration tutorial](https://docs.opencv.org/4.13.0/dc/dbb/tutorial_py_calibration.html)

No physical camera calibration was performed here. The focal value 600 is an arithmetic example, not a calibration file to copy.

## 5. Is low reprojection error enough?

It measures pixel differences between projected known points and detected corners. A low overall mean can hide poor edge behavior or a few bad views. Inspect per-image errors and held-out pattern poses.

If 20 mm squares are incorrectly declared as 25 mm, image agreement can remain good while translations have the wrong scale. Pixel agreement alone does not prove metric correctness.

## 6. Resize and crop change K

Halving a 640×480 image halves pixel intrinsics: fx/fy=300, cx=160, cy=120, and `(380,216)` becomes `(190,108)`. Cropping 40 pixels left and 20 top afterward changes the principal point to `(120,100)`.

For resize → crop → pad:

```text
fx' = sx fx                 fy' = sy fy
cx' = sx cx - crop_left + pad_left
cy' = sy cy - crop_top  + pad_top
```

Order matters. If undistortion produced a new camera matrix, use that as the starting matrix for subsequent changes. A purely pixel-based policy might not consume K explicitly, but geometry over processed images must use consistent intrinsics.

## 7. Fixed and wrist cameras

A fixed camera's base transform is constant while its mount stays unchanged. A wrist camera moves:

```text
T_base_camera(q) = T_base_wrist(q) T_wrist_camera
```

Estimating the camera-to-robot attachment using robot motion and pattern observations is hand-eye calibration. OpenCV provides `calibrateHandEye`; verify input/output transform directions in its contract. [Hand-eye API](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html)

Start by documenting each camera's role. Front should see the work area; wrist should help with approach/closure. More examples of a completely occluded object do not reveal it.

## 8. Does VLA require explicit calibration?

A policy can learn joint actions from image/state demonstrations without an explicit K/T pipeline. Camera arrangement still matters: changed height, field of view, crop, focus and exposure shift its inputs.

For the first VLA exercise, prioritize stable repeatable views, visibility and timing. Add measured intrinsics/extrinsics when doing analytic localization or camera simulation matching.

## 9. Save a camera card

Copy `templates/camera-card.json` and fill it with measured resolution/FPS, device identity, focus/exposure behavior, mounting photo path, units, transform direction and calibration date. Keep unknown values unknown.

**Completion:** rebuild the mount and compare a reference image; explain numerically why old K cannot be reused after arbitrary cropping. Physical calibration requires your own captured observations and validation views.
