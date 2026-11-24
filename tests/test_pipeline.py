import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "src" / "process_events.py"
spec = importlib.util.spec_from_file_location("event_pipeline", MODULE_PATH)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class TransformEventsTests(unittest.TestCase):
    def setUp(self):
        self.valid = {"event_id": "E1", "event_type": "order_created",
                      "event_timestamp": "2025-01-01T12:00:00Z", "customer_id": "C1",
                      "amount": "25.50", "source": "test"}

    def transform(self, event):
        return pipeline.transform_events([event])

    def test_accepts_valid_event(self):
        valid, rejected = self.transform(self.valid)
        self.assertEqual(len(valid), 1)
        self.assertEqual(rejected, [])
        self.assertEqual(valid[0]["amount"], "25.50")

    def test_rejects_duplicate_event_id(self):
        valid, rejected = pipeline.transform_events([self.valid, self.valid])
        self.assertEqual(len(valid), 1)
        self.assertEqual(rejected[0]["reason"], "duplicate_event_id")

    def test_rejects_negative_amount(self):
        _, rejected = self.transform({**self.valid, "amount": "-1"})
        self.assertEqual(rejected[0]["reason"], "negative_amount")

    def test_rejects_non_finite_amount(self):
        _, rejected = self.transform({**self.valid, "amount": "NaN"})
        self.assertEqual(rejected[0]["reason"], "invalid_timestamp_or_amount")

    def test_rejects_invalid_timestamp(self):
        _, rejected = self.transform({**self.valid, "event_timestamp": "not-a-date"})
        self.assertEqual(rejected[0]["reason"], "invalid_timestamp_or_amount")

    def test_rejects_missing_fields(self):
        row = dict(self.valid)
        del row["source"]
        _, rejected = self.transform(row)
        self.assertTrue(rejected[0]["reason"].startswith("missing_fields:"))

    def test_rejects_blank_customer(self):
        _, rejected = self.transform({**self.valid, "customer_id": " "})
        self.assertEqual(rejected[0]["reason"], "empty_customer_id")

    def test_rejects_non_object_event(self):
        valid, rejected = pipeline.transform_events([None])
        self.assertEqual(valid, [])
        self.assertEqual(rejected[0]["reason"], "event_not_object")

    def test_rejects_non_array_payload(self):
        with self.assertRaises(ValueError):
            pipeline.transform_events({"event_id": "E1"})

    def test_empty_csv_has_headers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "empty.csv"
            pipeline.write_csv(target, [], ["event_id", "reason"])
            with target.open(encoding="utf-8", newline="") as handle:
                self.assertEqual(next(csv.reader(handle)), ["event_id", "reason"])


if __name__ == "__main__":
    unittest.main()
