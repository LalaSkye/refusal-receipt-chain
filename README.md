# refusal-receipt-chain

A minimal public proof artefact for refusal receipts.

This repo shows one narrow thing:

> An attempted consequence-producing action must leave a receipt-bearing decision.

If the action is allowed, the receipt records why consequence was permitted to bind.

If the action is denied, the receipt records why consequence did not bind.

A refusal is not proven until it leaves a replayable receipt.

---

## What this contains

| File | Purpose |
|---|---|
| `receipt_schema_v0.1.json` | Minimal JSON Schema for ALLOW / DENY / HOLD receipts |
| `sample_allow_receipt.json` | Example receipt where authority and admissibility permit consequence to bind |
| `sample_deny_receipt.json` | Example receipt where missing authority prevents consequence from binding |
| `replay.py` | Minimal verifier that recomputes the receipt hash and checks the decision rule |

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

## Claim boundary

This repo proves only a minimal refusal receipt chain.

It does not prove:

- production enforcement
- full AI governance
- compliance
- adoption
- standard status
- complete consequence-governance architecture

It is a small proof surface:

> receipt schema → ALLOW / DENY examples → replay verifier

---

## Clean line

Language can describe a boundary.

Only an artefact can prove it stops.
