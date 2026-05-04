import copy
import unittest

from adapter import protected_action
from adapter.enforcement_adapter import enforce, current_policy_hash
from tests.test_receipts import load_json
import replay


class EnforcementAdapterTests(unittest.TestCase):
    def setUp(self):
        protected_action.reset_effect_log()
        self.action = load_json("adapter/sample_action_request.json")
        self.allow = load_json("sample_allow_receipt.json")
        self.deny = load_json("sample_deny_receipt.json")
        self.hold = load_json("sample_hold_receipt.json")

    def test_allow_receipt_executes_protected_action(self):
        result = enforce(self.action, self.allow)

        self.assertEqual(result["adapter_state"], "EXECUTED")
        self.assertTrue(result["effect_bound"])
        self.assertEqual(len(protected_action.EFFECT_LOG), 1)

    def test_missing_receipt_is_not_accepted_by_adapter_interface(self):
        with self.assertRaises(AttributeError):
            enforce(self.action, None)  # type: ignore[arg-type]
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_deny_receipt_blocks_protected_action(self):
        deny_action = copy.deepcopy(self.action)
        deny_action["actor_id"] = self.deny["actor_id"]
        result = enforce(deny_action, self.deny)

        self.assertEqual(result["adapter_state"], "BLOCKED")
        self.assertFalse(result["effect_bound"])
        self.assertEqual(result["reason"], "RECEIPT_NOT_ALLOW")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_hold_receipt_blocks_protected_action(self):
        hold_action = copy.deepcopy(self.action)
        hold_action["actor_id"] = self.hold["actor_id"]
        result = enforce(hold_action, self.hold)

        self.assertEqual(result["adapter_state"], "BLOCKED")
        self.assertFalse(result["effect_bound"])
        self.assertEqual(result["reason"], "RECEIPT_NOT_ALLOW")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_tampered_receipt_blocks(self):
        bad = copy.deepcopy(self.allow)
        bad["decision_reason_text"] = "Tampered text."
        result = enforce(self.action, bad)

        self.assertEqual(result["adapter_state"], "BLOCKED")
        self.assertFalse(result["effect_bound"])
        self.assertEqual(result["reason"], "RECEIPT_REPLAY_INVALID")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_policy_hash_mismatch_blocks(self):
        bad = copy.deepcopy(self.allow)
        bad["policy_hash"] = "sha256:" + "0" * 64
        bad["receipt_hash"] = replay.sha256_receipt_body(bad)

        result = enforce(self.action, bad)

        self.assertEqual(result["adapter_state"], "BLOCKED")
        self.assertFalse(result["effect_bound"])
        self.assertEqual(result["reason"], "POLICY_HASH_MISMATCH")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_action_type_mismatch_blocks(self):
        bad_action = copy.deepcopy(self.action)
        bad_action["action_type"] = "DELETE_RECORD"

        result = enforce(bad_action, self.allow)

        self.assertEqual(result["adapter_state"], "BLOCKED")
        self.assertFalse(result["effect_bound"])
        self.assertEqual(result["reason"], "ACTION_TYPE_MISMATCH")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_actor_mismatch_blocks(self):
        bad_action = copy.deepcopy(self.action)
        bad_action["actor_id"] = "different-actor"

        result = enforce(bad_action, self.allow)

        self.assertEqual(result["adapter_state"], "BLOCKED")
        self.assertFalse(result["effect_bound"])
        self.assertEqual(result["reason"], "ACTOR_MISMATCH")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_protected_action_direct_call_without_token_fails(self):
        with self.assertRaises(PermissionError):
            protected_action.write_record(self.action, release_token="")
        self.assertEqual(protected_action.EFFECT_LOG, [])

    def test_current_policy_hash_matches_allow_receipt(self):
        self.assertEqual(current_policy_hash(), self.allow["policy_hash"])


if __name__ == "__main__":
    unittest.main()
