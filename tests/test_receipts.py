import copy
import json
import unittest
from pathlib import Path

import jsonschema

import replay

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ReceiptValidationTests(unittest.TestCase):
    def setUp(self):
        self.schema = load_json("receipt_schema_v0.1.json")
        self.allow = load_json("sample_allow_receipt.json")
        self.deny = load_json("sample_deny_receipt.json")

    def assert_schema_valid(self, receipt):
        jsonschema.Draft7Validator.check_schema(self.schema)
        jsonschema.validate(instance=receipt, schema=self.schema)

    def assert_replay_valid(self, receipt):
        self.assertEqual(replay.validate_receipt(receipt), [])

    def test_allow_receipt_validates(self):
        self.assert_schema_valid(self.allow)
        self.assert_replay_valid(self.allow)
        self.assertEqual(self.allow["decision_state"], "ALLOW")
        self.assertTrue(self.allow["consequence_bound"])
        self.assertNotIn("refusal_effect", self.allow)

    def test_deny_receipt_validates(self):
        self.assert_schema_valid(self.deny)
        self.assert_replay_valid(self.deny)
        self.assertEqual(self.deny["decision_state"], "DENY")
        self.assertFalse(self.deny["consequence_bound"])
        self.assertEqual(self.deny["refusal_effect"], "ACTION_NOT_EXECUTED")

    def test_receipt_chain_links_deny_to_allow(self):
        self.assertEqual(
            self.deny["previous_receipt_hash"],
            self.allow["receipt_hash"],
        )

    def test_allow_with_missing_authority_fails(self):
        bad = copy.deepcopy(self.allow)
        bad["authority_state"] = "MISSING"
        bad["receipt_hash"] = replay.sha256_receipt_body(bad)

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=self.schema)

        self.assertNotEqual(replay.validate_receipt(bad), [])

    def test_deny_without_refusal_effect_fails(self):
        bad = copy.deepcopy(self.deny)
        bad.pop("refusal_effect")
        bad["receipt_hash"] = replay.sha256_receipt_body(bad)

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=self.schema)

        self.assertNotEqual(replay.validate_receipt(bad), [])

    def test_deny_with_consequence_bound_true_fails(self):
        bad = copy.deepcopy(self.deny)
        bad["consequence_bound"] = True
        bad["receipt_hash"] = replay.sha256_receipt_body(bad)

        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=self.schema)

        self.assertNotEqual(replay.validate_receipt(bad), [])


if __name__ == "__main__":
    unittest.main()
