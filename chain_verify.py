#!/usr/bin/env python3
"""
Chain verifier for refusal-receipt-chain v0.1.

Given an ordered list of receipt JSON files, this checks:
1. Each receipt's receipt_hash matches its canonical body (sha256 over body
   with receipt_hash removed).
2. Each receipt's previous_receipt_hash equals the prior receipt's
   receipt_hash. The first receipt may have previous_receipt_hash = null.

Scope:
This proves only that an ordered set of receipts links cleanly by hash.
It does not prove total path control, production enforcement, or that any
real-world action was physically prevented. A separate enforcement adapter
would be required to prove consequence-producing actions cannot bypass the
receipt boundary.

Usage:
    python chain_verify.py receipt1.json receipt2.json receipt3.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def canonical_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_receipt_body(receipt: Dict[str, Any]) -> str:
    body = dict(receipt)
    body.pop("receipt_hash", None)
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def verify_chain(receipts: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    prev_hash: Optional[str] = None

    for index, receipt in enumerate(receipts):
        computed = sha256_receipt_body(receipt)
        stored = receipt.get("receipt_hash")
        if stored != computed:
            errors.append(
                f"receipt[{index}] receipt_hash mismatch: "
                f"expected {computed}, found {stored}"
            )

        link = receipt.get("previous_receipt_hash")
        if index == 0:
            if link not in (None, ""):
                # First receipt may declare a prior link; that is allowed but
                # cannot be verified from inside this chain. Record as info.
                pass
        else:
            if link != prev_hash:
                errors.append(
                    f"receipt[{index}] previous_receipt_hash mismatch: "
                    f"expected {prev_hash}, found {link}"
                )

        prev_hash = stored

    return errors


def load_receipts(paths: List[Path]) -> List[Dict[str, Any]]:
    receipts: List[Dict[str, Any]] = []
    for path in paths:
        receipts.append(json.loads(path.read_text(encoding="utf-8")))
    return receipts


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an ordered chain of refusal receipts."
    )
    parser.add_argument(
        "receipts",
        nargs="+",
        type=Path,
        help="Ordered list of receipt JSON files",
    )
    args = parser.parse_args()

    try:
        receipts = load_receipts(args.receipts)
    except Exception as exc:
        print(f"ERROR: could not load receipts: {exc}", file=sys.stderr)
        return 2

    errors = verify_chain(receipts)
    if errors:
        print("CHAIN INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CHAIN VALID")
    print(f"length: {len(receipts)}")
    for index, receipt in enumerate(receipts):
        print(
            f"  [{index}] {receipt.get('receipt_id')} "
            f"{receipt.get('decision_state')} {receipt.get('receipt_hash')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
