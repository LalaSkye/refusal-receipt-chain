# refusal-receipt-chain

**Proof surface, not a safety system.**

This repo demonstrates post-hoc verification of refusal receipts. It does not claim live interception, production deployment, compliance, prevention, or external audit.

A minimal public proof artefact for refusal receipts.

This repo shows one narrow thing:

> An attempted consequence-producing action must leave a receipt-bearing decision.

If the action is allowed, the receipt records why consequence was permitted to bind.

If the action is denied, the receipt records why consequence did not bind.

If the action is held, the receipt records why consequence cannot bind yet.

A refusal is not proven until it leaves a replayable receipt.

---

## What this contains

| File | Purpose |
|---|---|
| `receipt_schema_v0.1.json` | Minimal JSON Schema for ALLOW / DENY / HOLD receipts (requires `schema_version` and `receipt_version`) |
| `policy-minimal-v0.1.json` | Minimal decision policy document referenced by `policy_id` and verified via `policy_hash` |
| `sample_allow_receipt.json` | Example receipt where authority and admissibility permit consequence to bind |
| `sample_deny_receipt.json` | Example receipt where missing authority prevents consequence from binding |
| `sample_hold_receipt.json` | Example receipt where unknown admissibility prevents consequence from binding yet |
| `replay.py` | Minimal verifier that recomputes the receipt hash and checks the decision rule |
| `chain_verify.py` | Chain verifier that checks ordered receipt hash linkage via `previous_receipt_hash` |
| `adapter/enforcement_adapter.py` | Minimal receipt-gated adapter that releases one protected action only for a valid ALLOW receipt |
| `adapter/protected_action.py` | Tiny protected action simulation with an in-memory effect log |
| `adapter/sample_action_request.json` | Example action request bound to the ALLOW receipt |
| `tests/test_receipts.py` | Positive and negative tests for schema, replay, consequence binding, refusal effect, tamper, and chain mismatch |
| `tests/test_chain_verify.py` | Positive and negative tests for chain hash linkage, tamper detection, ordering, and body corruption |
| `tests/test_enforcement_adapter.py` | Positive and negative tests for the receipt-gated adapter path |
| `requirements.txt` | Pinned dependency: `jsonschema>=4.0.0,<5.0.0` |
| `.github/workflows/ci.yml` | CI workflow for replay checks, chain verification, adapter execution, and validation tests |
| `CHANGELOG.md` | Version history |

---

## Core invariant

No consequence-producing action executes without a receipt-bearing decision.

---

## Versioning

Each receipt carries two version fields:

- `schema_version`: the version of the receipt schema (`"0.1"`)
- `receipt_version`: the version of the receipt format (`"0.1"`)

These are required by the schema and included in the receipt hash computation. Any future schema change increments `schema_version`; any future receipt format change increments `receipt_version`.

---

## Policy document

`policy-minimal-v0.1.json` contains the decision rules referenced by `policy_id: "policy-minimal-v0.1"` in all sample receipts.

Each receipt includes a `policy_hash` computed as `sha256(canonical_json(policy_document))`. This binds the receipt to the exact policy version that was applied at decision time. If the policy document changes, the `policy_hash` changes, and receipts can be checked against the policy they claim.

---

## Decision states

| State | Meaning |
|---|---|
| `ALLOW` | Authority is valid and the action is admissible; consequence may bind |
| `DENY` | Authority or admissibility fails; consequence must not bind |
| `HOLD` | Required state or evidence is unknown; consequence must not bind |

---

## Minimal decision rule

`ALLOW` only if:
- `authority_state = VALID`
- `admissibility_state = ADMISSIBLE`

`DENY` if:
- `authority_state = INVALID / MISSING / EXPIRED`
- or `admissibility_state = INADMISSIBLE`

`HOLD` if:
- `admissibility_state = UNKNOWN`
- or required evidence is unavailable

---

## Replay

Run:

```bash
python replay.py sample_allow_receipt.json
python replay.py sample_deny_receipt.json
python replay.py sample_hold_receipt.json
```

Expected result:

```text
VALID
```

The verifier checks:

1. `receipt_hash` matches the canonical receipt body.
2. `decision_state` matches the minimal decision rule.
3. `DENY` and `HOLD` receipts do not bind consequence.
4. `DENY` receipts include a refusal effect.

---

## Chain verification

`chain_verify.py` accepts an ordered list of receipt JSON files and checks:

1. Each receipt's `receipt_hash` matches its canonical body.
2. Each receipt's `previous_receipt_hash` equals the prior receipt's `receipt_hash`.
3. The first receipt may have `previous_receipt_hash = null`.

Run:

```bash
python chain_verify.py sample_allow_receipt.json sample_deny_receipt.json sample_hold_receipt.json
```

Expected result:

```text
CHAIN VALID
```

This proves only that an ordered set of receipts links cleanly by hash. It does not prove total path control.

---

## Minimal receipt-gated adapter

`adapter/enforcement_adapter.py` shows a tiny local adapter path:

```text
action request + receipt -> adapter -> protected action
```

The adapter releases the protected action only when:

- the receipt replays as valid
- `policy_hash` matches the current policy document
- `action_type` matches the action request
- `actor_id` matches the action request
- `decision_state = ALLOW`
- `consequence_bound = true`

Run:

```bash
python -m adapter.enforcement_adapter adapter/sample_action_request.json sample_allow_receipt.json
```

Expected result:

```text
"adapter_state": "EXECUTED"
```

The adapter blocks:

- DENY receipts
- HOLD receipts
- tampered receipts
- policy hash mismatch
- action type mismatch
- actor mismatch
- direct protected-action calls without the adapter release token

This proves only a minimal receipt-gated local action path. It does not prove that all possible consequence-producing paths are forced through the adapter.

---

## What hashes prove

The `receipt_hash` proves **receipt integrity**: the receipt body has not been altered since it was produced. It does not prove **external truth**: the hash does not prove that the described real-world action was actually attempted, that the actor existed, or that the stated consequence was physically prevented.

The `policy_hash` proves that the receipt references a specific, immutable version of the policy document. It does not prove that the policy was correctly applied at runtime.

The `previous_receipt_hash` proves chain ordering: the receipt was produced after the receipt it references. It does not prove that no receipts were omitted between them.

In summary: hashes prove receipt integrity and chain linkage. They do not prove external truth, completeness, or physical enforcement.

---

## Tests

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python -m unittest discover -s tests -t .
```

The tests check:

- valid ALLOW receipt
- valid DENY receipt
- valid HOLD receipt
- receipt chain links ALLOW → DENY → HOLD
- ALLOW with missing authority fails
- DENY without `refusal_effect` fails
- DENY with `consequence_bound=true` fails
- HOLD with known admissibility fails
- tampered receipt body fails hash replay
- chain mismatch is detectable by comparing expected previous receipt hash
- ordered chain validates via `chain_verify`
- first receipt with `previous_receipt_hash = null` is accepted
- tampered middle receipt breaks chain linkage
- out-of-order chain is detected
- corrupted receipt body hash mismatch is detected
- ALLOW receipt executes the local protected action through the adapter
- DENY and HOLD receipts block the local protected action
- tampered receipt blocks execution
- policy hash mismatch blocks execution
- action type mismatch blocks execution
- actor mismatch blocks execution
- direct protected-action call without adapter release token fails

---

## Claim boundary

This repo proves a minimal replayable receipt layer for ALLOW / DENY / HOLD decisions.

It proves that receipt objects can be checked, replayed, chain-verified, and used by a minimal local adapter to gate one protected action at the size it claims.

This repo does not prove that all consequence paths are forced through this receipt chain or adapter.

This repo does not prove production enforcement or physical prevention. It proves only that the local protected-action simulation refuses to run without the adapter release condition.

It does not prove:

- total path control
- production enforcement
- physical prevention
- full AI governance
- compliance
- adoption
- standard status
- complete consequence-governance architecture

It is a small proof surface:

> receipt schema → policy document → ALLOW / DENY / HOLD examples → replay verifier → chain verifier → receipt-gated adapter → tests → CI

---

## Future directions

Possible future artefacts (not in scope for v0.1):

- **Signed receipts (v0.2)**: add cryptographic signatures to receipts so that receipt authorship and integrity can be verified against a known public key, not just by hash.
- **Stronger enforcement adapter**: prove that a larger class of consequence-producing paths cannot bypass the receipt boundary.
- **Chain continuity verifier**: extend `chain_verify.py` to detect gaps in receipt sequences.

---

## Clean line

Language can describe a boundary.
Only an artefact can prove it stops.
