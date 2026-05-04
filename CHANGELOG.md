# Changelog

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
