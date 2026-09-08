"""Episode sızıntısı ve kinematik sayısal tutarlılığı için bağımsız kontroller."""
from pathlib import Path
import runpy
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
windows = runpy.run_path(str(ROOT / "examples/10_action_windows.py"))["build_windows"]
kin = runpy.run_path(str(ROOT / "examples/12_planar_ik.py"))


class LearningExamplesTests(unittest.TestCase):
    def test_window_never_uses_next_episode(self):
        rows = [{"episode_index": ep, "frame_index": i,
                 "action": [value], "observation.state": [0.]}
                for ep, values in [(0, [1, 2]), (1, [100, 200])]
                for i, value in enumerate(values)]
        batch = windows(list(reversed(rows)), 3)
        np.testing.assert_array_equal(batch["actions"][0, :, 0], [1, 2, 2])
        np.testing.assert_array_equal(batch["actions"][1, :, 0], [2, 2, 2])
        np.testing.assert_array_equal(batch["action_is_pad"][1], [False, True, True])
        np.testing.assert_array_equal(batch["actions"][2, :, 0], [100, 200, 200])

    def test_bad_sequence_and_nan_fail_before_training(self):
        row = {"episode_index": 0, "frame_index": 0, "action": [1.], "observation.state": [0.]}
        with self.assertRaises(ValueError):
            windows([row, {**row, "frame_index": 2}], 3)
        with self.assertRaises(ValueError):
            windows([{**row, "action": [float("nan")]}], 3)

    def test_ik_round_trip_multiple_targets_and_unreachable(self):
        for target in [[.22, .10], [.18, .14], [-.20, .05], [.32, 0]]:
            for q in kin["ik"](*target):
                np.testing.assert_allclose(kin["fk"](q), target, atol=1e-12)
        for target in [[.4, 0], [0, 0], [float("inf"), 0]]:
            with self.assertRaises(ValueError):
                kin["ik"](*target)


if __name__ == "__main__":
    unittest.main()
