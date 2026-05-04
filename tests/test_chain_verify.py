"""Tests for chain_verify.py.

Covers:
- positive: ordered ALLOW -> DENY -> HOLD chain validates
- positive: first receipt with previous_receipt_hash = null is accepted
- negative: a tampered (re-hashed) middle receipt breaks the previous_receipt_hash linkage detected by the next receipt
- negative: receipts presented out of order are detected as a chain mismatch
- negative: a corrupted receipt body whose receipt_hash no longer matches is detected
"""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import chain_verify

REPO_ROOT = Path(__file__).resolve().parent.parent
ALLOW = REPO_ROOT / "sample_allow_receipt.json"
DENY = REPO_ROOT / "sample_deny_receipt.json"
HOLD = REPO_ROOT / "sample_hold_receipt.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def rehash(receipt):
    receipt = dict(receipt)
    receipt.pop("receipt_hash", None)
    canonical = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    receipt["receipt_hash"] = f"sha256:{digest}"
    return receipt


class TestChainVerify(unittest.TestCase):
    def test_ordered_chain_validates(self):
        receipts = [load(ALLOW), load(DENY), load(HOLD)]
        errors = chain_verify.verify_chain(receipts)
        self.assertEqual(errors, [], f"unexpected errors: {errors}")

    def test_first_receipt_null_previous_hash_allowed(self):
        allow = load(ALLOW)
        allow_null = copy.deepcopy(allow)
        allow_null["previous_receipt_hash"] = None
        allow_null = rehash(allow_null)
        errors = chain_verify.verify_chain([allow_null])
        self.assertEqual(errors, [], f"unexpected errors: {errors}")

    def test_tampered_middle_receipt_breaks_link(self):
        allow = load(ALLOW)
        deny = load(DENY)
        hold = load(HOLD)

        tampered_deny = copy.deepcopy(deny)
        tampered_deny["decision_reason_text"] = "TAMPERED"
        tampered_deny = rehash(tampered_deny)

        # HOLD's previous_receipt_hash still points at the original DENY hash,
        # so the chain link from tampered_deny to hold must fail.
        errors = chain_verify.verify_chain([allow, tampered_deny, hold])
        self.assertTrue(
            any("previous_receipt_hash mismatch" in e for e in errors),
            f"expected previous_receipt_hash mismatch in errors: {errors}",
        )

    def test_out_of_order_chain_detected(self):
        receipts = [load(DENY), load(ALLOW), load(HOLD)]
        errors = chain_verify.verify_chain(receipts)
        self.assertTrue(
            any("previous_receipt_hash mismatch" in e for e in errors),
            f"expected mismatch when chain is out of order: {errors}",
        )

    def test_corrupted_body_hash_mismatch(self):
        allow = load(ALLOW)
        corrupted = copy.deepcopy(allow)
        corrupted["decision_reason_text"] = "CORRUPTED"
        # Note: receipt_hash NOT recomputed, so it must mismatch the body.
        errors = chain_verify.verify_chain([corrupted])
        self.assertTrue(
            any("receipt_hash mismatch" in e for e in errors),
            f"expected receipt_hash mismatch: {errors}",
        )


if __name__ == "__main__":
    unittest.main()
