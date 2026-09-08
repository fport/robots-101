"""Veri/komut araçlarının kritik sözleşme kontrolleri; robot gerektirmez."""
import importlib.util
import json
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
training = runpy.run_path(str(ROOT / "examples/05_prepare_training.py"))
evaluation = runpy.run_path(str(ROOT / "examples/06_evaluate_results.py"))


def metadata():
    return {"total_episodes": 10, "total_frames": 60, "fps": 30, "features": {
        "observation.state": {"dtype": "float32", "shape": [6]},
        "action": {"dtype": "float32", "shape": [6]},
        "observation.images.front": {"dtype": "video", "shape": [480, 640, 3],
                                     "names": ["height", "width", "channels"]},
    }}


class TrainingContractTests(unittest.TestCase):
    def test_real_camera_shape_and_no_invented_cameras(self):
        features = training["policy_features"](metadata())
        self.assertEqual(features["observation.images.front"]["shape"], [3, 480, 640])
        self.assertEqual(set(features), {"observation.state", "observation.images.front"})

    def test_rejects_other_embodiment_and_no_camera(self):
        info = metadata()
        info["features"]["action"]["shape"] = [7]
        with self.assertRaises(ValueError):
            training["policy_features"](info)
        info = metadata()
        del info["features"]["observation.images.front"]
        with self.assertRaises(ValueError):
            training["policy_features"](info)

    def test_insufficient_eval_data_is_not_silent(self):
        info = metadata()
        info["total_episodes"] = 3
        with self.assertRaisesRegex(ValueError, "yeterli episode"):
            training["make_command"](info, "/tmp/data", "local/test", "/tmp/out")

    def test_command_is_local_and_uses_dataset_schema(self):
        args = training["make_command"](metadata(), "/tmp/data space", "local/test", "/tmp/out")
        self.assertIn("--dataset.root=/tmp/data space", args)
        self.assertIn("--policy.push_to_hub=false", args)
        self.assertIn("--policy.path=lerobot/smolvla_base", args)
        self.assertFalse(any(arg.startswith("--job.target=") for arg in args))
        raw = next(arg.split("=", 1)[1] for arg in args if arg.startswith("--policy.input_features="))
        self.assertEqual(set(json.loads(raw)), {"observation.state", "observation.images.front"})

    @unittest.skipUnless(importlib.util.find_spec("lerobot"), "LeRobot yalnız ML ortamında")
    def test_generated_features_parse_with_installed_smolvla_config(self):
        import draccus
        from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig
        cfg = draccus.parse(SmolVLAConfig, args=[
            "--device=cpu", "--push_to_hub=false",
            "--input_features=" + json.dumps(training["policy_features"](metadata())),
        ])
        cfg.validate_features()
        self.assertEqual(tuple(cfg.input_features["observation.images.front"].shape), (3, 480, 640))


class EvaluationTests(unittest.TestCase):
    def test_small_sample_uncertainty_is_visible(self):
        rows = [{"episode_id": str(i), "success": "1", "failure_reason": ""} for i in range(3)]
        report = evaluation["summarize"](rows)
        self.assertEqual(report["success_rate"], 1)
        self.assertLess(report["wilson_95_percent"][0], .5)
        self.assertAlmostEqual(report["wilson_95_percent"][1], 1)

    def test_invalid_and_duplicate_results_fail(self):
        with self.assertRaises(ValueError):
            evaluation["summarize"]([])
        row = {"episode_id": "1", "success": "1", "failure_reason": ""}
        with self.assertRaises(ValueError):
            evaluation["summarize"]([row, row])
        with self.assertRaises(ValueError):
            evaluation["summarize"]([{**row, "success": ""}])
        with self.assertRaises(ValueError):
            evaluation["summarize"]([{**row, "success": "0"}])


@unittest.skipUnless(importlib.util.find_spec("pyarrow"), "Parquet testleri ML ortamında")
class DatasetIntegrityTests(unittest.TestCase):
    def test_corrupt_timestamp_and_shape_are_detected(self):
        import pyarrow as pa
        import pyarrow.parquet as pq
        inspect_dataset = runpy.run_path(str(ROOT / "examples/04_inspect_dataset.py"))["inspect_dataset"]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "meta").mkdir()
            (root / "data").mkdir()
            info = metadata()
            info.update(total_episodes=2, total_frames=6)
            (root / "meta/info.json").write_text(json.dumps(info))
            rows = [{"episode_index": ep, "frame_index": i, "timestamp": i/30,
                     "observation.state": [0.]*6, "action": [0.]*6} for ep in range(2) for i in range(3)]
            target = root / "data/test.parquet"
            pq.write_table(pa.Table.from_pylist(rows), target)
            self.assertEqual(inspect_dataset(root, 2)["errors"], [])
            rows[-1]["timestamp"] = 999
            rows[-1]["action"] = [float("nan")]*5
            pq.write_table(pa.Table.from_pylist(rows), target)
            self.assertGreaterEqual(len(inspect_dataset(root, 2)["errors"]), 2)


if __name__ == "__main__":
    unittest.main()
