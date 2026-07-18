# Dependency Graph

Sprint: TANTRA Ecosystem Participation

---

## Runtime execution dependency chain

```
POST /runtime/ecosystem/execute
│
└─ service/ecosystem_runtime.py :: execute_ecosystem_runtime()
   │
   ├─ kosha/deterministic_pipeline.py :: run_deterministic_pipeline()
   │   └─ (internal: retrieval, constitutional_runtime, semantic_memory)
   │
   ├─ governance/constitutional_runtime.py :: ConstitutionalCognitionRuntime.execute()
   │   └─ (local — no external dependency)
   │
   ├─ integrations/tantra_sdk_adapter.py :: TantraSdkAdapter.emit_execution_event()
   │   └─ (local payload builder — no HTTP)
   │
   ├─ integrations/tantra_runtime_client.py :: TantraRuntimeClient
   │   ├─ submit_execution_event()  →  TANTRA_SDK_BASE_URL/runtime/execution-event
   │   ├─ submit_trace()            →  TANTRA_SDK_BASE_URL/runtime/trace
   │   └─ validate_authority()      →  TANTRA_SDK_BASE_URL/runtime/authority/validate
   │
   ├─ integrations/bucket_telemetry.py :: BucketTelemetryClient.emit()
   │   └─ UNIGURU_BUCKET_TELEMETRY_ENDPOINT
   │
   ├─ integrations/insightflow_client.py :: InsightFlowClient
   │   ├─ emit_trace()    →  INSIGHTFLOW_BASE_URL/traces
   │   └─ emit_decision() →  INSIGHTFLOW_BASE_URL/decisions
   │
   ├─ integrations/gc_client.py :: GCClient
   │   ├─ validate_authority()    →  GC_BASE_URL/gc/validate/authority
   │   └─ validate_hidden_state() →  GC_BASE_URL/gc/validate/hidden-state
   │
   └─ integrations/mdu_client.py :: MDUClient
       ├─ validate_schema()     →  MDU_BASE_URL/mdu/validate/schema
       └─ validate_provenance() →  MDU_BASE_URL/mdu/validate/provenance
```

---

## Env var → client mapping

| Env var prefix | Client | Phase |
|----------------|--------|-------|
| `TANTRA_SDK_*` | `TantraRuntimeClient` | Phase 1 — Vijay SDK |
| `UNIGURU_BUCKET_TELEMETRY_*` | `BucketTelemetryClient` | Phase 2 — Bucket |
| `INSIGHTFLOW_*` | `InsightFlowClient` | Phase 3 — InsightFlow |
| `GC_*` | `GCClient` | Phase 4 — GC |
| `MDU_*` | `MDUClient` | Phase 4 — MDU |

---

## No circular dependencies

All new clients are leaf nodes — they make outbound HTTP calls only and have no imports
from other UniGuru modules. They can be tested in isolation.
