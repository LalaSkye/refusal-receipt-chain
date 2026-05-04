"""Minimal protected action simulation.

This module deliberately models one tiny consequence-producing action: writing a
record into an in-memory effect log. It is not production enforcement.
"""
from __future__ import annotations

from typing import Any, Dict, List


EFFECT_LOG: List[Dict[str, Any]] = []


def reset_effect_log() -> None:
    """Clear the in-memory effect log."""
    EFFECT_LOG.clear()


def write_record(action_request: Dict[str, Any], release_token: str) -> Dict[str, Any]:
    """Write one record only when the adapter supplies a valid release token."""
    if release_token != "ALLOW_RECEIPT_VERIFIED":
        raise PermissionError("protected action requires verified ALLOW receipt")

    effect = {
        "effect_type": "WRITE_RECORD",
        "request_id": action_request["request_id"],
        "payload": action_request.get("payload", {}),
    }
    EFFECT_LOG.append(effect)
    return effect
