# Architecture Map
## UniGuru BHIV Ecosystem Integration

**Generated:** 2026-07-10

---

## System Architecture

```mermaid
flowchart TD
    subgraph BHIV["BHIV / TANTRA Ecosystem"]
        MITRA["Mitra / BHIV\n(External caller)"]
        VIJAY["Vijay\n(Runtime replay authority)"]
        BUCKET["Bucket Team\n(Live telemetry)"]
        INSIGHT["InsightFlow Team\n(Trace ingestion)"]
        GC["GC Team\n(Constitutional authority)"]
        MDU["MDU Team\n(Schema & provenance)"]
    end

    subgraph UNIGURU["UniGuru Runtime (backend/)"]
        RTAPI["uniguru_runtime_api.py\nPOST /runtime/ecosystem/execute\nPOST /runtime/ecosystem/replay\nPOST /mitra/ecosystem/ask\nGET /health, /ready, /metrics"]
        ECORUNTIME["ecosystem_runtime.py\nexecute_ecosystem_runtime()\nverify_ecosystem_replay()"]
        KOSHA["kosha/deterministic_pipeline.py\nrun_deterministic_pipeline()"]
        GOVRT["governance/constitutional_runtime.py\nConstitutionalCognitionRuntime.execute()"]
        MEMORY["memory/constitutional_semantic_memory.py\nstable_hash(), utc_now_iso()"]
        BUCKET_CLIENT["integrations/bucket_telemetry.py\nBucketTelemetryClient.emit()"]
        MDU_CONTRACT["contracts/runtime_evidence_contract.json\nMDU required field schema"]
    end

    MITRA -->|"POST /mitra/ecosystem/ask\nor POST /runtime/ecosystem/execute"| RTAPI
    RTAPI --> ECORUNTIME
    ECORUNTIME -->|"1. Kosha pipeline"| KOSHA
    ECORUNTIME -->|"2. Vijay replay validation"| GOVRT
    GOVRT -->|"stable_hash()"| MEMORY
    ECORUNTIME -->|"3. Bucket telemetry"| BUCKET_CLIENT
    ECORUNTIME -->|"4. InsightFlow trace hash"| MEMORY
    ECORUNTIME -->|"5. GC authority check"| GOVRT
    ECORUNTIME -->|"6. MDU schema validation"| MDU_CONTRACT
    ECORUNTIME -->|"7. TANTRA contract binding"| KOSHA

    RTAPI -->|"Governed redacted response"| MITRA
    GOVRT -.->|"Vijay_validation block\nruntime_hash, replay_safe,\nlast_event_hash"| VIJAY
    BUCKET_CLIENT -.->|"File-backed in local;\nHTTP POST in BHIV deployment"| BUCKET
    MEMORY -.->|"trace_hash"| INSIGHT
    GOVRT -.->|"canonical_authority_granted"| GC
    MDU_CONTRACT -.->|"evidence_payload\nlineage_hash"| MDU
```

---

## Integration Touchpoints

| # | Touchpoint | Mechanism | Evidence Field |
|---|-----------|-----------|----------------|
| 1 | **Vijay – Runtime Replay** | `ConstitutionalCognitionRuntime.execute()` with `vijay_runtime` arbitrator | `vijay_validation.replay_safe`, `vijay_validation.runtime_hash` |
| 2 | **Bucket – Telemetry** | `BucketTelemetryClient` (file-backed locally; HTTP in BHIV) | `bucket_telemetry.emitted`, `bucket_telemetry.bucket_path` |
| 3 | **InsightFlow – Observability** | `stable_hash(trace_id + runtime_hash)` as trace fingerprint | `insightflow_observability.trace_hash`, `trace_complete` |
| 4 | **GC – Authority Validation** | `ConstitutionalCognitionRuntime` authority enforcement | `gc_validation.authority_enforced`, `canonical_authority_granted` |
| 5 | **MDU – Schema & Provenance** | Field validation against `contracts/runtime_evidence_contract.json` | `mdu_validation.schema_compatible`, `evidence_payload.lineage_hash` |
| 6 | **TANTRA – Contract Binding** | Output contract from Kosha pipeline | `tantra_contract.contract_bound`, `downstream_consumable` |
| 7 | **Mitra – Governed Interface** | Redacted response (no internal governance payloads) | `replay_safe`, `answer`, `verification_status`, `downstream_consumable` |

---

## Data Flow: Execute → Replay → Mitra

```
POST /runtime/ecosystem/execute
  → run_deterministic_pipeline(query)          [Kosha]
  → _build_vijay_validation()                  [ConstitutionalCognitionRuntime]
  → _build_bucket_telemetry()                  [BucketTelemetryClient / file]
  → _build_tantra_contract()                   [Kosha output_contract]
  → _build_insightflow_observability()         [stable_hash]
  → _build_gc_validation()                     [authority_enforced check]
  → _build_mdu_validation()                    [runtime_evidence_contract.json]
  → stable_hash(full_payload) → execution_hash
  → write integration_proof/ecosystem_execution_{trace_id}.json

POST /runtime/ecosystem/replay
  → execute_ecosystem_runtime() × 2 (same trace_id)
  → compare: runtime_hash, last_event_hash, lineage_hash, contract_schema
  → replay_verified = all checks pass

POST /mitra/ecosystem/ask
  → execute_ecosystem_runtime()
  → strip: vijay_validation, gc_validation, mdu_validation
  → return: trace_id, answer, verification_status, replay_safe, contract_schema
```
