# Threat Model

## Scope

This repo demonstrates post-hoc verification of refusal receipts.

It protects against:

- unverifiable refusal claims
- missing refusal records
- silent receipt alteration
- broken receipt ordering
- policy mismatch after the fact

It does not protect against:

- live unsafe action execution
- model misbehaviour
- sandbox escape
- compromised runtime authority
- production system failure
- malicious operators with full repository control

## Threat model

The assumed threat is simple:

A system claims it refused an unsafe or unauthorised action, but there is no inspectable evidence that the refusal occurred, matched a policy, produced no mutation, and remained unchanged later.

This repo tests whether a refusal can be recorded as a receipt, bound to a policy hash, linked into a chain, and replayed for verification.

## Claim boundary

This is a proof surface, not a deployed safety system.
