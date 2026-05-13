# refusal-receipt-chain

## Public disclosure boundary

This repository is a public inspection surface, not full architecture disclosure.

It shows a bounded claim, minimal receipt examples, an inspection path, and the claim limit.

See [`PUBLIC_DISCLOSURE_BOUNDARY.md`](PUBLIC_DISCLOSURE_BOUNDARY.md).

## What this repo is

A minimal public proof surface for replayable ALLOW / DENY / HOLD receipt objects.

It demonstrates one narrow claim:

> A receipt object can be checked, replayed, and used to show why a local demonstrated decision did or did not permit consequence.

## What this does not prove

This repository does not prove live interception, production deployment, compliance, external audit, physical prevention, complete path control, or full AI governance.

It does not prove that all consequence-producing paths are forced through this receipt layer.

It is a local proof object only.

## Inspection path

Run the receipt checks and tests:

```bash
python replay.py sample_allow_receipt.json
python replay.py sample_deny_receipt.json
python replay.py sample_hold_receipt.json
python -m unittest discover -s tests -t .
```

Expected result classes:

```text
VALID
BLOCKED
```

## What this proves

On the demonstrated path:

- receipt objects can be checked and replayed
- receipt hash tampering is detectable
- DENY and HOLD receipts do not permit consequence in the local demonstration
- an ALLOW receipt can permit the local demonstrated action
- chain linkage can be checked for the sample receipt sequence

## What hashes prove

Hashes prove receipt integrity and sample chain linkage.

They do not prove external truth, completeness, physical enforcement, or production control.

## Claim boundary

This repo proves only the local receipt-checking behaviour attached to this public proof object.

It must not be treated as a map of the wider system, a deployment model, or proof of complete consequence-governance architecture.

## Licence

MIT.
