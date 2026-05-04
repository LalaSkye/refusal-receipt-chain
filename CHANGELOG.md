# Changelog

## v0.1.1 — 2026-05-04

Hardening patch: policy document, version fields, hash integrity documentation.

### Added

- `policy-minimal-v0.1.json` — minimal decision policy document; `policy_hash` in receipts now verifiable against this file
- `schema_version` and `receipt_version` fields — required in schema and all sample receipts; included in receipt hash computation
- "What hashes prove" README section — clarifies hashes prove receipt integrity and chain linkage, not external truth, completeness, or physical enforcement
- "Versioning" README section — documents `schema_version` and `receipt_version` semantics
- "Policy document" README section — documents `policy_hash` binding
- "Future directions" README section — notes signed receipts (v0.2), enforcement adapter, and chain continuity verifier as out-of-scope future artefacts

### Changed

- `receipt_schema_v0.1.json` — added `schema_version` (const `"0.1"`) and `receipt_version` (const `"0.1"`) as required properties
- `sample_allow_receipt.json` — added version fields, updated `policy_hash` to match `policy-minimal-v0.1.json`, recomputed `receipt_hash`
- `sample_deny_receipt.json` — added version fields, updated `policy_hash`, `previous_receipt_hash`, recomputed `receipt_hash`
- `sample_hold_receipt.json` — added version fields, updated `policy_hash`, `previous_receipt_hash`, recomputed `receipt_hash`
- `README.md` — added policy, versioning, hash integrity, and future directions sections; updated file table and proof surface line

### Claim boundary

This repo proves a minimal replayable receipt layer for ALLOW / DENY / HOLD decisions.
It does not prove total path control, production enforcement, physical prevention, full AI governance, compliance, adoption, or standard status.
Hashes prove receipt integrity and chain linkage. They do not prove external truth.

---

## v0.1 — 2026-05-04

Initial hardened proof artefact.

### Added

- `receipt_schema_v0.1.json` — minimal JSON Schema for ALLOW / DENY / HOLD receipts
- `sample_allow_receipt.json` — ALLOW example
- `sample_deny_receipt.json` — DENY example
- `sample_hold_receipt.json` — HOLD example
- `replay.py` — single-receipt replay verifier (hash + decision rule + consequence binding)
- `chain_verify.py` — ordered chain verifier (receipt hash linkage via `previous_receipt_hash`)
- `tests/test_receipts.py` — positive and negative receipt validation tests
- `tests/test_chain_verify.py` — positive and negative chain linkage tests
- `requirements.txt` — pinned `jsonschema>=4.0.0,<5.0.0`
- `.github/workflows/ci.yml` — CI: replay all receipts, verify chain, run tests
- `README.md` — claim boundary, chain verification docs, physical prevention disclaimer

### Claim boundary

This repo proves a minimal replayable receipt layer for ALLOW / DENY / HOLD decisions.
It does not prove total path control, production enforcement, physical prevention, full AI governance, compliance, adoption, or standard status.
