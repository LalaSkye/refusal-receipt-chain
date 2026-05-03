#!/usr/bin/env python3
"""
Replay verifier for refusal-receipt-chain v0.1.

This checks three things:
1. receipt_hash matches the canonical receipt body.
2. decision_state matches the minimal decision rule.
3. DENY / HOLD receipts do not bind consequence.

Usage:
    python replay.py sample_allow_receipt.json
    python replay.py sample_deny_receipt.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict


AUTHORITY_DENY_STATES = {"INVALID", "MISSING", "EXPIRED"}


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_receipt_body(receipt: Dict[str, Any]) -> str:
    body = dict(receipt)
    body.pop("receipt_hash", None)
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def expected_decision(receipt: Dict[str, Any]) -> str:
    authority = receipt.get("authority_state")
    admissibility = receipt.get("admissibility_state")

    if authority == "VALID" and admissibility == "ADMISSIBLE":
        return "ALLOW"
    if authority in AUTHORITY_DENY_STATES or admissibility == "INADMISSIBLE":
        return "DENY"
    if admissibility == "UNKNOWN":
        return "HOLD"
    return "HOLD"


def validate_receipt(receipt: Dict[str, Any]) -> list[str]:
    errors: list[str] = []

    computed_hash = sha256_receipt_body(receipt)
    if receipt.get("receipt_hash") != computed_hash:
        errors.append(
            f"receipt_hash mismatch: expected {computed_hash}, found {receipt.get('receipt_hash')}"
        )

    expected = expected_decision(receipt)
    actual = receipt.get("decision_state")
    if actual != expected:
        errors.append(f"decision_state mismatch: expected {expected}, found {actual}")

    consequence_bound = receipt.get("consequence_bound")
    if actual == "ALLOW" and consequence_bound is not True:
        errors.append("ALLOW receipt must set consequence_bound=true")

    if actual in {"DENY", "HOLD"} and consequence_bound is not False:
        errors.append("DENY/HOLD receipt must set consequence_bound=false")

    if actual == "DENY" and not receipt.get("refusal_effect"):
        errors.append("DENY receipt must include refusal_effect")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Replay and verify a refusal receipt.")
    parser.add_argument("receipt", type=Path, help="Path to receipt JSON file")
    args = parser.parse_args()

    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: could not read receipt: {exc}", file=sys.stderr)
        return 2

    errors = validate_receipt(receipt)

    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    print(f"receipt_id: {receipt['receipt_id']}")
    print(f"decision_state: {receipt['decision_state']}")
    print(f"consequence_bound: {receipt['consequence_bound']}")
    print(f"receipt_hash: {receipt['receipt_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
