# Reviewer Notes

Sprint: TANTRA Ecosystem Participation

---

## For Vijay Dhawan (TANTRA SDK & Runtime Owner)

### Contract path assumptions

The following endpoint paths were assumed from the task specification. Vijay must confirm
or correct them before the live integration can be certified:

| Contract | Assumed path |
|----------|-------------|
| Runtime Contract | `POST /runtime/execution-event` |
| Replay Contract | `POST /runtime/replay-event` |
| Trace Contract | `POST /runtime/trace` |
| Authority Contract | `POST /runtime/authority/validate` |
| Capability Contract | `POST /runtime/capability/register` |

If the actual paths differ, update `TantraRuntimeClient` method bodies only — the
calling code in `ecosystem_runtime.py` does not need to change.

### Payload schema

The execution event payload is built by `TantraSdkAdapter.emit_execution_event()` and
conforms to `execution_event.v1.0.0`. If Vijay's runtime expects a different schema
version or field names, update `TantraSdkAdapter` — do not duplicate the schema.

---

## For GC Team

The authority validation payload sent to `/gc/validate/authority` contains:
```json
{
  "trace_id": "...",
  "authority_enforced": true/false,
  "canonical_authority_granted": true/false,
  "governance_note": "..."
}
```

The hidden-state payload sent to `/gc/validate/hidden-state` contains:
```json
{
  "trace_id": "...",
  "runtime_hash": "..."
}
```

If GC expects additional fields, add them to `_build_gc_validation` in `ecosystem_runtime.py`.

---

## For MDU Team

The schema validation payload sent to `/mdu/validate/schema` is the full `evidence_payload`
conforming to `runtime_evidence_contract.json`. The provenance payload sent to
`/mdu/validate/provenance` is the `lineage_payload` containing `trace_id`, `runtime_hash`,
`retrieval_hash`, and `interpretation_hash`.

---

## For InsightFlow Owner

Traces are emitted to `/traces`, decisions to `/decisions`. Both payloads include `trace_id`
as the primary correlation key. If InsightFlow requires a different correlation field name,
update `InsightFlowClient` method bodies.

---

## General notes

- No governance logic was modified. `ConstitutionalCognitionRuntime` is unchanged.
- No duplicate schemas were introduced. `runtime_evidence_contract.json` is the single source.
- All new clients follow the same pattern as the existing `BucketTelemetryClient`.
- Replay determinism is preserved: live client responses are attached to the payload but
  do not affect the `execution_hash` computation (live responses vary per call).
- The `execution_hash` is computed over the deterministic fields only, not over live responses.

**Note on execution_hash and live responses:**
Currently `stable_hash(payload)` is called after all live responses are attached to `payload`.
This means the execution hash will vary if live services return different responses.
Vijay should confirm whether the hash should be computed before or after live responses
are attached. If before, move `payload["execution_hash"] = stable_hash(payload)` to before
the live client calls, or exclude live response fields from the hash input.
