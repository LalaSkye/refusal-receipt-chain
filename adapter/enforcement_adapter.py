#!/usr/bin/env python3
"""Minimal receipt-gated enforcement adapter v0.1.

This adapter shows one narrow thing:
A protected action is only released when a receipt is valid and its decision_state is ALLOW.

Scope:
This is a local proof artefact. It does not prove production enforcement, total path
control, physical prevention, compliance, adoption, or that every real-world action
path is forced through this adapter.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

import replay
from adapter import protected_action

REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy-minimal-v0.1.json"


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_json(data: Dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def current_policy_hash() -> str:
    return sha256_json(load_json(POLICY_PATH))


def deny(reason: str, receipt_id: str | None = None) -> Dict[str, Any]:
    return {
        "adapter_state": "BLOCKED",
        "effect_bound": False,
        "receipt_id": receipt_id,
        "reason": reason,
    }


def enforce(action_request: Dict[str, Any], receipt: Dict[str, Any]) -> Dict[str, Any]:
    """Release a protected action only when an ALLOW receipt verifies."""
    receipt_id = receipt.get("receipt_id")

    replay_errors = replay.validate_receipt(receipt)
    if replay_errors:
        return deny("RECEIPT_REPLAY_INVALID", receipt_id)

    if receipt.get("policy_hash") != current_policy_hash():
        return deny("POLICY_HASH_MISMATCH", receipt_id)

    if receipt.get("action_type") != action_request.get("action_type"):
        return deny("ACTION_TYPE_MISMATCH", receipt_id)

    if receipt.get("actor_id") != action_request.get("actor_id"):
        return deny("ACTOR_MISMATCH", receipt_id)

    if receipt.get("decision_state") != "ALLOW":
        return deny("RECEIPT_NOT_ALLOW", receipt_id)

    if receipt.get("consequence_bound") is not True:
        return deny("ALLOW_RECEIPT_DID_NOT_BIND_CONSEQUENCE", receipt_id)

    effect = protected_action.write_record(action_request, "ALLOW_RECEIPT_VERIFIED")
    return {
        "adapter_state": "EXECUTED",
        "effect_bound": True,
        "receipt_id": receipt_id,
        "reason": "ALLOW_RECEIPT_VERIFIED",
        "effect": effect,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run minimal receipt-gated adapter.")
    parser.add_argument("action_request", type=Path, help="Path to action request JSON")
    parser.add_argument("receipt", type=Path, help="Path to receipt JSON")
    args = parser.parse_args()

    try:
        action_request = load_json(args.action_request)
        receipt = load_json(args.receipt)
    except Exception as exc:
        print(f"ERROR: could not load inputs: {exc}", file=sys.stderr)
        return 2

    result = enforce(action_request, receipt)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["adapter_state"] == "EXECUTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
