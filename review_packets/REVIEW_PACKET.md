# REVIEW_PACKET.md — UniGuru TANTRA Ecosystem Integration

Generated at: `2026-07-11`
Sprint: TANTRA Ecosystem Participation
Status: `INTEGRATION_WIRED — PENDING_LIVE_ENDPOINT_CREDENTIALS`

---

## 1. Scope

This sprint wires UniGuru into the canonical TANTRA ecosystem runtime so every execution
participates in the full chain:

```
User → UniGuru → TANTRA → Vijay SDK → Bucket → InsightFlow → GC → MDU → Mitra → Replay
```

All local-only validators have been replaced with live HTTP clients that are env-gated.
When endpoint credentials are provided by Vijay / GC / MDU / InsightFlow teams, the
clients activate automatically — no code changes required.

---

## 2. Integration Architecture

### New files added

| File | Purpose |
|------|---------|
| `backend/integrations/tantra_runtime_client.py` | Live Vijay SDK — Runtime, Replay, Trace, Authority, Capability contracts |
| `backend/integrations/insightflow_client.py` | Live InsightFlow — traces, decisions, metrics, failures |
| `backend/integrations/gc_client.py` | Live GC — authority, hidden-state, governance-drift validation |
| `backend/integrations/mdu_client.py` | Live MDU — schema, provenance, replay-lineage validation |

### Modified files

| File | Change |
|------|--------|
| `backend/integrations/__init__.py` | Exports all four new clients |
| `backend/service/ecosystem_runtime.py` | Wires live clients into all 7 integration layers |
| `backend/integrations/bucket_telemetry.py` | Unchanged — already has live HTTP emission |
| `backend/.env.example` | Added all ecosystem endpoint env vars |

---

## 3. Environment Variables Required

Obtain values from the respective service owners before enabling:

```
# Vijay TANTRA SDK
TANTRA_SDK_ENABLED=true
TANTRA_SDK_BASE_URL=https://<tantra-sdk-host>/api/v1
TANTRA_SDK_TOKEN=<token>

# Bucket
UNIGURU_BUCKET_TELEMETRY_ENABLED=true
UNIGURU_BUCKET_TELEMETRY_ENDPOINT=https://<bucket-host>/api/v1/events
UNIGURU_BUCKET_TELEMETRY_TOKEN=<token>

# InsightFlow
INSIGHTFLOW_ENABLED=true
INSIGHTFLOW_BASE_URL=https://<insightflow-host>/api/v1
INSIGHTFLOW_TOKEN=<token>

# GC
GC_ENABLED=true
GC_BASE_URL=https://<gc-host>/api/v1
GC_TOKEN=<token>

# MDU
MDU_ENABLED=true
MDU_BASE_URL=https://<mdu-host>/api/v1
MDU_TOKEN=<token>
```

---

## 4. Integration Layer Status

| Layer | Client | Live HTTP | Env Gate | Status |
|-------|--------|-----------|----------|--------|
| Vijay SDK — Runtime Contract | `TantraRuntimeClient.submit_execution_event` | ✅ | `TANTRA_SDK_ENABLED` | Wired, awaiting credentials |
| Vijay SDK — Replay Contract | `TantraRuntimeClient.submit_replay_event` | ✅ | `TANTRA_SDK_ENABLED` | Wired, awaiting credentials |
| Vijay SDK — Trace Contract | `TantraRuntimeClient.submit_trace` | ✅ | `TANTRA_SDK_ENABLED` | Wired, awaiting credentials |
| Vijay SDK — Authority Contract | `TantraRuntimeClient.validate_authority` | ✅ | `TANTRA_SDK_ENABLED` | Wired, awaiting credentials |
| Bucket | `BucketTelemetryClient.emit` | ✅ | `UNIGURU_BUCKET_TELEMETRY_ENABLED` | Wired, awaiting credentials |
| InsightFlow — Trace | `InsightFlowClient.emit_trace` | ✅ | `INSIGHTFLOW_ENABLED` | Wired, awaiting credentials |
| InsightFlow — Decision | `InsightFlowClient.emit_decision` | ✅ | `INSIGHTFLOW_ENABLED` | Wired, awaiting credentials |
| GC — Authority | `GCClient.validate_authority` | ✅ | `GC_ENABLED` | Wired, awaiting credentials |
| GC — Hidden State | `GCClient.validate_hidden_state` | ✅ | `GC_ENABLED` | Wired, awaiting credentials |
| MDU — Schema | `MDUClient.validate_schema` | ✅ | `MDU_ENABLED` | Wired to `GET /api/v1/datasets/canonical/{canonical_id}` using the live BHIV MDU contract |
| MDU — Provenance | `MDUClient.validate_provenance` | ✅ | `MDU_ENABLED` | Wired to the same canonical dataset lookup path for provenance continuity evidence |

---

## 5. Execution Flow

```
POST /runtime/ecosystem/execute
  └─ execute_ecosystem_runtime()
       ├─ run_deterministic_pipeline()          # Kosha + constitutional reasoning
       ├─ _build_vijay_validation()             # Local constitutional hash + replay safety
       ├─ _build_bucket_telemetry()             # Local proof + live Bucket HTTP emit
       ├─ _build_tantra_contract()              # TANTRA contract fields
       ├─ _build_insightflow_observability()    # Local state + live InsightFlow HTTP emit
       ├─ _build_gc_validation()               # Local authority check + live GC HTTP validate
       ├─ _build_mdu_validation()              # Local schema check + live MDU HTTP validate
       └─ _build_tantra_sdk_contracts()        # Local event + live TANTRA SDK HTTP submit
```

---

## 6. Coordination Required (Mandatory)

This sprint **cannot be self-certified**. The following must be completed jointly with Vijay:

- [ ] Vijay provides `TANTRA_SDK_BASE_URL` and `TANTRA_SDK_TOKEN`
- [ ] Vijay confirms contract endpoint paths (`/runtime/execution-event`, `/runtime/trace`, etc.)
- [ ] GC team provides `GC_BASE_URL` and `GC_TOKEN`
- [ ] MDU team provides `MDU_BASE_URL` and `MDU_TOKEN`
- [ ] InsightFlow owner provides `INSIGHTFLOW_BASE_URL` and `INSIGHTFLOW_TOKEN`
- [ ] Bucket owner provides `UNIGURU_BUCKET_TELEMETRY_ENDPOINT` and token
- [ ] Joint replay verification run with Vijay after credentials are live
- [ ] Cross-service trace ID confirmed in InsightFlow dashboard
- [ ] GC authority validation response confirmed
- [ ] MDU schema validation response confirmed

---

## 7. Screenshots

Screenshots must be captured after live credentials are configured and a real execution run
is performed. Store under `review_packets/screenshots/` with the following structure:

```
screenshots/
  runtime/
    ecosystem_execute.png        # POST /runtime/ecosystem/execute response
    replay_verification.png      # POST /runtime/ecosystem/replay response
  integrations/
    tantra_sdk_response.png      # Live TANTRA SDK acknowledgement
    bucket_telemetry.png         # Bucket event acknowledgement
    insightflow_trace.png        # InsightFlow trace dashboard
    gc_validation.png            # GC authority validation response
    mdu_validation.png           # MDU schema validation response
  deployment/
    health_check.png             # GET /health response
    metrics.png                  # GET /metrics output
```

Screenshots cannot be fabricated. They must show real HTTP responses from live services.

---

## 8. Self-Validation Checklist

- [ ] `TANTRA_SDK_ENABLED=true` and execution event reaches Vijay's runtime
- [ ] `UNIGURU_BUCKET_TELEMETRY_ENABLED=true` and bucket acknowledges events
- [ ] `INSIGHTFLOW_ENABLED=true` and traces appear in InsightFlow dashboard
- [ ] `GC_ENABLED=true` and authority validation returns a governed response
- [ ] `MDU_ENABLED=true` and schema validation returns a compatibility verdict from the live BHIV MDU canonical dataset endpoint
- [ ] Replay produces identical `runtime_hash` and `lineage_hash` across two runs
- [ ] No local validator remains where a live service endpoint exists
- [ ] No mocked responses in production execution path
