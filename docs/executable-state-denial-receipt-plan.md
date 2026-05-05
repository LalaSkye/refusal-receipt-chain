# Executable State Denial Receipt — Build Plan

## Verdict

Build `executable-state-denial-receipt` first.

It answers the load-bearing question directly:

> Where does execution become unavailable?

`admissibility-field-schema` and `admissibility-failure-test-vectors` are useful, but they are scaffolding. The denial receipt creates the artefact they can later formalise and attack.

---

## Ranked builds

### 1. executable-state-denial-receipt

Purpose: receipt emitted at the exact point where admissibility fails and no executable state is created.

Proof surface:

- failing admissibility field(s)
- `executable_state_created = false`
- typed negative-evidence proof
- previous receipt hash
- canonical receipt hash

Claim boundary:

This proves a minimal receipt schema and replayable examples for non-bind cases. It does not prove production enforcement, complete admissibility coverage, governance of a calling system, adoption, certification, or compliance.

### 2. admissibility-field-schema

Purpose: closed v0.1 schema for the five-field admissibility envelope.

Fields:

- authority
- scope
- evidence
- state
- time

### 3. admissibility-failure-test-vectors

Purpose: hostile and near-miss test vectors against the denial receipt and admissibility field schema.

---

## Recommended first artefact

Suggested repo:

`LalaSkye/executable-state-denial-receipt`

Suggested file layout:

```text
executable-state-denial-receipt/
├── README.md
├── schema/
│   └── denial_receipt_v0.1.json
├── samples/
│   ├── sample_deny_authority_missing.json
│   └── sample_hold_evidence_unresolved.json
├── replay.py
└── LICENSE
```

---

## README skeleton

```md
# executable-state-denial-receipt

Minimal public proof artefact. Produces a receipt at the exact point where execution became unavailable.

## What this is

A schema and replayable example for the receipt emitted when admissibility fails and no executable state is created for a requested action.

This artefact shows one narrow thing:

When admissibility fails, the system must produce a receipt that:

- names the failing admissibility field(s)
- carries proof that no executable state was created
- chains to a prior receipt by sha256 prev-hash
- is byte-replayable on a clean clone

## Claim boundary

This repo proves only:

1. A schema for receipts emitted at the execution-boundary refusal point.
2. One replayable example per failure class.
3. A hash-chain link to an upstream receipt.

It does not prove:

- production enforcement
- complete admissibility coverage
- that the upstream verifier is correct
- that the calling system is governed
- adoption, certification, or compliance

## Replay

python replay.py samples/sample_deny_authority_missing.json
python replay.py samples/sample_hold_evidence_unresolved.json

Expected output for both: `VALID`.

## Clean line

Language can describe a boundary. Only an artefact can prove execution did not bind.
```

---

## Schema skeleton

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ExecutableStateDenialReceipt",
  "type": "object",
  "required": [
    "schema_version",
    "receipt_id",
    "in_reply_to",
    "decision_state",
    "authority_state",
    "scope_state",
    "evidence_state",
    "state_condition",
    "time_condition",
    "failing_fields",
    "executable_state_created",
    "non_executable_state_proof",
    "previous_receipt_hash",
    "receipt_hash",
    "emitted_at"
  ],
  "properties": {
    "schema_version": { "const": "v0.1" },
    "receipt_id": { "type": "string", "pattern": "^[a-f0-9]{16}$" },
    "in_reply_to": { "type": "string" },
    "decision_state": { "enum": ["DENY", "HOLD"] },
    "authority_state": { "enum": ["VALID", "INVALID", "MISSING", "EXPIRED"] },
    "scope_state": { "enum": ["APPLICABLE", "OUT_OF_SCOPE", "UNRESOLVED"] },
    "evidence_state": { "enum": ["ADMISSIBLE", "INADMISSIBLE", "STALE", "UNKNOWN"] },
    "state_condition": { "enum": ["SATISFIED", "UNSATISFIED", "UNRESOLVED"] },
    "time_condition": { "enum": ["IN_WINDOW", "OUT_OF_WINDOW", "UNRESOLVED"] },
    "failing_fields": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": { "enum": ["authority", "scope", "evidence", "state", "time"] }
    },
    "executable_state_created": { "const": false },
    "non_executable_state_proof": {
      "type": "object",
      "required": ["kind", "before", "after", "equal"],
      "properties": {
        "kind": {
          "enum": [
            "state_store_unwritten",
            "subprocess_not_spawned",
            "queue_unmodified",
            "filesystem_untouched",
            "network_call_not_issued"
          ]
        },
        "before": { "type": "string" },
        "after": { "type": "string" },
        "equal": { "const": true }
      }
    },
    "previous_receipt_hash": {
      "type": "string",
      "pattern": "^(genesis|sha256:[a-f0-9]{64})$"
    },
    "receipt_hash": {
      "type": "string",
      "pattern": "^sha256:[a-f0-9]{64}$"
    },
    "emitted_at": { "type": "string", "format": "date-time" }
  }
}
```

---

## Public claim limit

`executable-state-denial-receipt` is a minimal public schema and replayable example for receipts emitted at the point where admissibility fails and no executable state is created. It carries typed negative-evidence proof and chains by sha256 to a prior receipt. It does not claim production enforcement, complete admissibility coverage, governance of any calling system, adoption, certification, or compliance.
