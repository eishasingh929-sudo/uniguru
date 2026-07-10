# Critical Execution Flow
## UniGuru BHIV Ecosystem – Maximum 3 Files

**Generated:** 2026-07-10

> This document traces the complete execution path from a BHIV request to a governed response across exactly three files.

---

## File 1: `backend/service/uniguru_runtime_api.py`
**Role:** FastAPI application and endpoint gateway

### Endpoint: `POST /runtime/ecosystem/execute`

```python
class EcosystemRuntimeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    emit_proof: bool = True
    trace_id: Optional[str] = None

    @field_validator("query")
    @classmethod
    def _normalize_query(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("query must not be empty or whitespace-only.")
        return normalized


@app.post("/runtime/ecosystem/execute")
def ecosystem_runtime_execute(request: EcosystemRuntimeRequest) -> Dict[str, Any]:
    return execute_ecosystem_runtime(
        query=request.query,
        emit_proof=request.emit_proof,
        trace_id=request.trace_id,
    )
```

**Key guarantees enforced at this layer:**
- Query whitespace normalization → invalid queries rejected with HTTP 422
- `trace_id` threaded through to enable deterministic replay
- `emit_proof=True` writes integration artefacts to `review_packets/integration_proof/`

---

## File 2: `backend/service/ecosystem_runtime.py`
**Role:** BHIV ecosystem orchestrator – the single canonical integration path

### `execute_ecosystem_runtime()` – full 7-stage pipeline

```python
def execute_ecosystem_runtime(query, proof_dir=None, emit_proof=True, trace_id=None):
    trace_id = trace_id or f"ecosystem_{uuid.uuid5(...)}"

    # Stage 1: Kosha deterministic pipeline (canonical retrieval)
    pipeline_result = run_deterministic_pipeline(query=query, trace_id=trace_id)

    # Stage 2: Vijay replay validation (ConstitutionalCognitionRuntime)
    vijay_validation = _build_vijay_validation(trace_id, pipeline_result, {})

    # Stage 3: Bucket telemetry (file-backed locally; HTTP in BHIV)
    bucket_telemetry = _build_bucket_telemetry(trace_id, pipeline_result, proof_dir)

    # Stage 4: TANTRA contract binding
    tantra_contract = _build_tantra_contract(trace_id, pipeline_result, bucket_telemetry)

    # Stage 5: InsightFlow observability (trace hash)
    insightflow_observability = _build_insightflow_observability(trace_id, pipeline_result, vijay_validation)

    # Stage 6: GC authority validation
    gc_validation = _build_gc_validation(vijay_validation, pipeline_result)

    # Stage 7: MDU schema and provenance validation
    mdu_validation = _build_mdu_validation(trace_id, pipeline_result, vijay_validation)

    payload = { trace_id, query, vijay_validation, tantra_contract,
                bucket_telemetry, insightflow_observability, gc_validation, mdu_validation }
    payload["execution_hash"] = stable_hash(payload)

    if emit_proof:
        _write_json(proof_dir / f"ecosystem_execution_{trace_id}.json", payload)
        _write_json(proof_dir / "ecosystem_execution_latest.json", payload)

    return payload
```

### Vijay Validation Detail (`_build_vijay_validation`)

```python
def _build_vijay_validation(trace_id, pipeline_result, runtime_trace):
    # Build semantic event for this execution
    semantic_event = {
        "trace_id": trace_id,
        "claim_key": "ecosystem_execution",
        "confidence": float(pipeline_result["confidence_breakdown"]["overall"]),
        "provenance_weight": 0.42,          # or 0.0 if unverified
        "legitimacy_evidence": 0.38,
        "reinforcement_count": len(pipeline_result["matched_signals"]),
        "contradiction_pressure": 0.0,       # or 0.35 if unverified
        ...
    }

    # Run ConstitutionalCognitionRuntime with vijay_runtime as primary arbitrator
    governance_result = ConstitutionalCognitionRuntime.execute(
        previous_snapshot=snapshot,
        current_snapshot=snapshot,
        semantic_events=[semantic_event],
        arbitrators=[{"node_id": "vijay_runtime"}, {"node_id": "isha_runtime"}],
        ...
    )

    # Extract replay-safe fields
    return {
        "trace_id": trace_id,
        "runtime_hash": governance_result["runtime_trace"]["runtime_hash"],
        "replay_safe": bool(governance_result["replay_flow"]["replay_safe"]),
        "last_event_hash": governance_result["replay_flow"]["last_event_hash"],
        "hash_chain_ok": governance_result["runtime_trace"]["event_registry_verification"]["hash_chain_ok"],
        "canonical_authority_granted": bool(governance_result["runtime_trace"]["canonical_authority_granted"]),
    }
```

### Replay Verification (`verify_ecosystem_replay`)

```python
def verify_ecosystem_replay(query, proof_dir=None, trace_id=None, emit_proof=True):
    # Execute twice with the SAME trace_id → must produce identical hashes
    first  = execute_ecosystem_runtime(query, proof_dir, emit_proof=False, trace_id=replay_trace_id)
    replay = execute_ecosystem_runtime(query, proof_dir, emit_proof=False, trace_id=replay_trace_id)

    checks = {
        "trace_id_stable":                 first["trace_id"] == replay["trace_id"],
        "vijay_runtime_hash_stable":       first["vijay_validation"]["runtime_hash"]
                                           == replay["vijay_validation"]["runtime_hash"],
        "vijay_last_event_hash_stable":    first["vijay_validation"]["last_event_hash"]
                                           == replay["vijay_validation"]["last_event_hash"],
        "tantra_contract_schema_stable":   first["tantra_contract"]["schema"]
                                           == replay["tantra_contract"]["schema"],
        "gc_authority_enforcement_stable": first["gc_validation"]["authority_enforced"]
                                           == replay["gc_validation"]["authority_enforced"],
        "mdu_lineage_hash_stable":         first["mdu_validation"]["evidence_payload"]["lineage_hash"]
                                           == replay["mdu_validation"]["evidence_payload"]["lineage_hash"],
    }
    return { "replay_verified": all(checks.values()), "checks": checks, ... }
```

---

## File 3: `backend/governance/constitutional_runtime.py`
**Role:** ConstitutionalCognitionRuntime – the canonical Vijay replay validation engine

This module implements the constitutional governance runtime that `ecosystem_runtime.py` calls for Vijay validation. It:

1. **Processes semantic events** – each execution becomes a governed semantic event with `trace_id`, `claim_key`, `confidence`, `provenance_weight`
2. **Runs trust propagation** – computes `trust_ceiling` and `authority_pressure_score` per claim
3. **Evaluates contradictions** – escalates unresolved contradictions, blocks silent merges
4. **Enforces ontology boundaries** – checks `legitimacy_ceiling` per domain
5. **Generates replay artifacts** – deterministic `runtime_hash` via `stable_hash()`, `last_event_hash`, `replay_safe` flag
6. **Returns component hashes** – all components produce independent hashes for chain verification

**Key output fields consumed by Vijay validation:**

```python
{
  "runtime_trace": {
    "runtime_hash":                   "sha256 of full execution state",
    "canonical_authority_granted":    False,   # constitutional ceiling
    "event_registry_verification": {
      "hash_chain_ok": True
    },
    "component_hashes": { ... }
  },
  "replay_flow": {
    "replay_safe":        True,        # identical re-execution produces same hash
    "last_event_hash":    "sha256..."  # fingerprint of last semantic event
  }
}
```

**Replay safety guarantee:** `stable_hash()` from `memory/constitutional_semantic_memory.py` uses SHA-256 over deterministically serialized JSON (sorted keys). Given the same inputs, outputs are always identical — this is the cryptographic foundation of Vijay's replay safety attestation.

---

## Execution Sequence Diagram

```
BHIV Caller
    │
    ▼
POST /runtime/ecosystem/execute           [uniguru_runtime_api.py]
    │ EcosystemRuntimeRequest validated
    │ trace_id assigned
    │
    ▼
execute_ecosystem_runtime()               [ecosystem_runtime.py]
    │
    ├─► run_deterministic_pipeline()       [kosha/deterministic_pipeline.py]
    │     └─ Returns: pipeline_result (signals, confidence, verification_status)
    │
    ├─► _build_vijay_validation()
    │     └─► ConstitutionalCognitionRuntime.execute()  [governance/constitutional_runtime.py]
    │           └─ Returns: runtime_hash ✓, replay_safe ✓, hash_chain_ok ✓
    │
    ├─► _build_bucket_telemetry()          → bucket_{trace_id}.json
    ├─► _build_tantra_contract()           → contract_bound ✓
    ├─► _build_insightflow_observability() → trace_hash, trace_complete ✓
    ├─► _build_gc_validation()             → authority_enforced ✓
    ├─► _build_mdu_validation()            → schema_compatible ✓, lineage_hash ✓
    │
    ├─► stable_hash(payload) → execution_hash
    ├─► write ecosystem_execution_{trace_id}.json
    └─► write ecosystem_execution_latest.json
    │
    ▼
Return full payload to caller
    │
    ▼ (if called via /mitra/ecosystem/ask)
Strip vijay_validation, gc_validation, mdu_validation
Return governed redacted response to Mitra
```
