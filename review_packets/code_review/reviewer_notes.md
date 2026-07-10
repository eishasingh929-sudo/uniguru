# Reviewer Notes
## UniGuru BHIV Ecosystem Integration

**Prepared for:** Vijay, Soham, Alay, and BHIV ecosystem review team
**Date:** 2026-07-10
**Status:** PRODUCTION READY

---

## What to Verify First

1. **Ecosystem acceptance verdict** — open `review_packets/validation_reports/ecosystem_acceptance_report.json`
   - `verdict` must be `"ACCEPTED"`
   - All 11 checks in the `checks` block must be `true`

2. **Vijay replay proof** — open `review_packets/integration_proof/replay_verification_latest.json`
   - `replay_verified` must be `true`
   - `checks.vijay_runtime_hash_stable` and `checks.vijay_last_event_hash_stable` must be `true`
   - The two `stable_fields.runtime_hash` values across both runs must be identical SHA-256 hashes

3. **Benchmark** — open `review_packets/proof_logs/benchmark_report.json`
   - `overall_pass` must be `true`
   - All 7 benchmark categories must show `PASS`

4. **Fault injection** — open `review_packets/proof_logs/fault_injection_report.json`
   - `verdict` must be `"ALL_PASS"` (6/6 tests)

5. **Stability** — open `review_packets/proof_logs/stability_report.json`
   - `verdict` must be `"STABLE"`
   - `errors` must be `0`
   - `latency_stats.drift_pct` must be `< 30%`

---

## Key Design Decisions

### 1. Vijay integration is canonical, not simulated
`_build_vijay_validation()` in `ecosystem_runtime.py` calls `ConstitutionalCognitionRuntime.execute()` directly — the same governance engine used throughout the UniGuru runtime. The `vijay_runtime` arbitrator is declared in the call. The output `runtime_hash` is a SHA-256 over the full governance state. Re-executing with the same `trace_id` produces the identical hash — this is the cryptographic replay proof.

**What Vijay's team should verify:** run `POST /runtime/ecosystem/replay` with any query and confirm `replay_verified: true` and that `vijay_runtime_hash_stable: true`.

### 2. Bucket telemetry is file-backed locally
`UNIGURU_BUCKET_TELEMETRY_ENABLED=false` in `.env.production` means the `BucketTelemetryClient` writes to `review_packets/integration_proof/bucket_{trace_id}.json` locally. In BHIV deployment, set:
```
UNIGURU_BUCKET_TELEMETRY_ENABLED=true
UNIGURU_BUCKET_TELEMETRY_ENDPOINT=<Bucket collector URL>
UNIGURU_BUCKET_TELEMETRY_TOKEN=<token>
```
The `bucket_telemetry.emitted` field is `true` in all local runs because the file write succeeds. HTTP emission activates transparently when the endpoint is configured — no code change required.

### 3. InsightFlow trace hash is deterministic
`insightflow_observability.trace_hash = stable_hash({trace_id, verification_status, runtime_hash})`. This ties InsightFlow's trace fingerprint to Vijay's runtime hash. The InsightFlow team can ingest this hash as the canonical trace identifier.

### 4. GC canonical authority is intentionally not granted
`gc_validation.canonical_authority_granted` is always `false`. This is constitutional design — UniGuru is an internal intelligence capability, not a canonical authority node. The GC validation confirms that authority enforcement is working correctly *by* denying canonical authority while still enforcing constitutional bounds.

### 5. MDU schema validation is contract-driven
`_build_mdu_validation()` reads `backend/contracts/runtime_evidence_contract.json` at runtime and validates every `evidence_payload` against its `required` field list. Adding MDU fields means updating that JSON file — no Python code change needed.

### 6. Mitra payload is structurally redacted
`/mitra/ecosystem/ask` strips `vijay_validation`, `gc_validation` and `mdu_validation` before returning. This is a structural guarantee enforced in `uniguru_runtime_api.py`, not a configuration flag. Reviewers can verify by running `POST /mitra/ecosystem/ask` and confirming those keys are absent from the response body.

---

## How to Re-Run All Validation

### Prerequisites
Python 3.12 installed at `C:\Users\Isha Singh\AppData\Local\Programs\Python\Python312\python.exe`
Required packages: `fastapi`, `uvicorn`, `pydantic`, `httpx`, `requests`, `pytest`

### Commands (run from repo root)

```powershell
# All unit tests (21 tests)
& "C:\Users\Isha Singh\AppData\Local\Programs\Python\Python312\python.exe" -m pytest

# Ecosystem acceptance (generates all review_packets/ artefacts)
& "C:\Users\Isha Singh\AppData\Local\Programs\Python\Python312\python.exe" scripts/run_ecosystem_acceptance.py

# Performance benchmark
& "C:\Users\Isha Singh\AppData\Local\Programs\Python\Python312\python.exe" scripts/benchmark_performance.py

# Fault injection (6 resilience tests)
& "C:\Users\Isha Singh\AppData\Local\Programs\Python\Python312\python.exe" scripts/run_fault_injection.py

# Stability (30-query long-duration validation)
& "C:\Users\Isha Singh\AppData\Local\Programs\Python\Python312\python.exe" scripts/run_stability_validation.py
```

---

## Known Limits

| Limit | Detail | Mitigation |
|-------|--------|-----------|
| Bucket telemetry is file-backed locally | No live HTTP emission without Bucket endpoint config | Set env vars in BHIV deployment – no code change |
| No external Vijay service URL | Vijay validation runs via embedded ConstitutionalCognitionRuntime | Hash-stable replay proof available via `/runtime/ecosystem/replay` |
| Screenshots are of local FastAPI /docs UI | No BHIV external UI available | API evidence captured via browser subagent against local server |
| Kosha knowledge base is Balbharti curriculum | Some test queries return NO_VERIFIED_KNOWLEDGE | Constitutional behaviour — system correctly refuses to hallucinate |
| node-backend/ absent | Node middleware not present in this checkout | Backend API is directly deployable via `uvicorn service.api:app` |

---

## Integration Map Summary

| Team | Integration Point | Status | Evidence |
|------|------------------|--------|----------|
| **Vijay** | `vijay_validation` block — `ConstitutionalCognitionRuntime` with `vijay_runtime` arbitrator | ✅ LIVE | `ecosystem_execution_latest.json → vijay_validation` |
| **Bucket** | `bucket_telemetry` — `BucketTelemetryClient` (file → HTTP) | ✅ FILE-BACKED (HTTP ready) | `bucket_ecosystem_acceptance_live.json` |
| **InsightFlow** | `insightflow_observability` — deterministic `trace_hash` | ✅ LIVE | `ecosystem_execution_latest.json → insightflow_observability` |
| **GC** | `gc_validation` — authority enforcement via constitutional runtime | ✅ LIVE | `ecosystem_execution_latest.json → gc_validation` |
| **MDU** | `mdu_validation` — schema + provenance via contract JSON | ✅ LIVE | `ecosystem_execution_latest.json → mdu_validation` |
| **Mitra** | `/mitra/ecosystem/ask` — governed redacted interface | ✅ LIVE | `ecosystem_acceptance_api_responses.json → mitra` |
