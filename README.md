# refusal-receipt-chain

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
| `receipt_schema_v0.1.json` | Minimal JSON Schema for ALLOW / DENY / HOLD receipts |
| `sample_allow_receipt.json` | Example receipt where authority and admissibility permit consequence to bind |
| `sample_deny_receipt.json` | Example receipt where missing authority prevents consequence from binding |
| `sample_hold_receipt.json` | Example receipt where unknown admissibility prevents consequence from binding yet |
| `replay.py` | Minimal verifier that recomputes the receipt hash and checks the decision rule |
| `chain_verify.py` | Chain verifier that checks ordered receipt hash linkage via `previous_receipt_hash` |
| `tests/test_receipts.py` | Positive and negative tests for schema, replay, consequence binding, refusal effect, tamper, and chain mismatch |
| `tests/test_chain_verify.py` | Positive and negative tests for chain hash linkage, tamper detection, ordering, and body corruption |
| `requirements.txt` | Pinned dependency: `jsonschema>=4.0.0,<5.0.0` |
| `.github/workflows/ci.yml` | CI workflow for replay checks, chain verification, and validation tests |
| `CHANGELOG.md` | Version history |

---

## Core invariant

No consequence-producing action executes without a receipt-bearing decision.

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

This proves only that an ordered set of receipts links cleanly by hash. It does not prove total path control. A separate enforcement adapter would be required to prove that consequence-producing actions cannot bypass the receipt boundary.

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

---

## Claim boundary

This repo proves a minimal replayable receipt layer for ALLOW / DENY / HOLD decisions.

It proves that receipt objects can be checked, replayed, and chain-verified at the size it claims.

This repo does not prove that all consequence paths are forced through this receipt chain.
A separate enforcement adapter would be required to prove that consequence-producing actions cannot bypass the receipt boundary.

This repo does not prove that the described external action was physically prevented; it proves only that the decision receipt records and replays the declared decision state.

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

> receipt schema → ALLOW / DENY / HOLD examples → replay verifier → chain verifier → tests → CI

---

## Clean line

Language can describe a boundary.
Only an artefact can prove it stops.
