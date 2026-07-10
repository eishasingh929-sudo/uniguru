# API Contracts
## UniGuru BHIV Ecosystem Runtime

**Base URL (local):** `http://127.0.0.1:8010`
**Base URL (production):** `https://uniguru-v2.onrender.com` *(after Render deployment)*
**Schema Version:** `UNIGURU_RUNTIME_RESPONSE_CONTRACT_V1`

---

## POST `/runtime/ecosystem/execute`

Full BHIV execution – returns all 7 integration touchpoints. Used by BHIV internal services.

### Request

```json
{
  "query": "string (1–2000 chars, non-whitespace-only)",
  "emit_proof": true,
  "trace_id": "string (optional – assigned if omitted)"
}
```

### Response (200 OK)

```json
{
  "trace_id": "ecosystem_abc123def456",
  "query": "What is the Bhagavad Gita?",
  "timestamp": "2026-07-10T18:07:53Z",
  "verification_status": "NO_VERIFIED_KNOWLEDGE | VERIFIED | PARTIAL_VERIFIED_SAMPLE",
  "confidence": 0.0,
  "answer": "I do not have a verified Balbharti curriculum record for this query yet.",

  "vijay_validation": {
    "trace_id": "ecosystem_abc123def456",
    "runtime_hash": "sha256hex",
    "replay_safe": true,
    "last_event_hash": "sha256hex",
    "hash_chain_ok": true,
    "canonical_authority_granted": false,
    "component_hashes": { ... },
    "semantic_event": { ... }
  },

  "tantra_contract": {
    "trace_id": "ecosystem_abc123def456",
    "schema": "TANTRA_UNIGURU_INTELLIGENCE_CONTRACT_V1",
    "contract_bound": true,
    "downstream_consumable": true,
    "verification_status": "NO_VERIFIED_KNOWLEDGE",
    "bucket_proof_ready": true,
    "trace_continuity": {
      "retrieval": "ecosystem_abc123def456",
      "validation": "ecosystem_abc123def456",
      "synthesis": "ecosystem_abc123def456",
      "bucket_proof": "ecosystem_abc123def456"
    }
  },

  "bucket_telemetry": {
    "event": "ecosystem_runtime_execution",
    "trace_id": "ecosystem_abc123def456",
    "route": "TANTRA_ECOSYSTEM",
    "verification_status": "NO_VERIFIED_KNOWLEDGE",
    "decision": "block | answer",
    "query_hash": "16_char_hash",
    "ontology_reference": { "domain": "...", "trace_id": "..." },
    "timestamp": "2026-07-10T18:07:53Z",
    "emitted": true,
    "bucket_path": "review_packets/integration_proof/bucket_ecosystem_abc123def456.json"
  },

  "insightflow_observability": {
    "trace_id": "ecosystem_abc123def456",
    "trace_complete": true,
    "trace_hash": "sha256hex",
    "observability_state": "live_runtime_trace_complete",
    "pipeline_status": "NO_VERIFIED_KNOWLEDGE",
    "replay_safe": true
  },

  "gc_validation": {
    "trace_id": "ecosystem_abc123def456",
    "authority_enforced": true,
    "canonical_authority_granted": false,
    "governance_note": "Constitutional authority remains read-only..."
  },

  "mdu_validation": {
    "trace_id": "ecosystem_abc123def456",
    "schema_compatible": true,
    "required_fields": ["evidence_id", "textbook_id", ...],
    "missing_fields": [],
    "evidence_payload": {
      "evidence_id": "uuid",
      "textbook_id": "bhiv_internal_intelligence_platform",
      "edition": "2026",
      "chapter": "ecosystem",
      "section": "runtime_convergence",
      "page_numbers": [1],
      "source_hash": "sha256hex",
      "retrieval_hash": "sha256hex",
      "lineage_hash": "sha256hex",
      "verification_status": "UNVERIFIED | VERIFIED | PARTIAL_VERIFIED_SAMPLE"
    },
    "provenance_continuity": true
  },

  "pipeline_summary": {
    "matched_signals": 0,
    "rejected_signals": 0,
    "domain": "null | Agriculture | ...",
    "reasoning_path": [...]
  },

  "execution_hash": "sha256hex"
}
```

### Error Responses

| Code | Condition |
|------|-----------|
| `422` | `query` is empty, whitespace-only, or exceeds 2000 characters |
| `500` | Internal pipeline error (should never occur in stable runtime) |

---

## POST `/runtime/ecosystem/replay`

Replay verification endpoint – executes the pipeline twice with the same `trace_id` and validates hash stability across Vijay, TANTRA, GC and MDU fields.

### Request
Same as `/runtime/ecosystem/execute`.

### Response (200 OK)

```json
{
  "schema": "UNIGURU_ECOSYSTEM_REPLAY_VERIFICATION_V1",
  "trace_id": "ecosystem_replay_abc123",
  "query_hash": "16_char_hash",
  "generated_at": "2026-07-10T18:07:53Z",
  "checks": {
    "trace_id_stable": true,
    "vijay_runtime_hash_stable": true,
    "vijay_last_event_hash_stable": true,
    "tantra_contract_schema_stable": true,
    "tantra_trace_continuity_stable": true,
    "gc_authority_enforcement_stable": true,
    "mdu_lineage_hash_stable": true
  },
  "replay_verified": true,
  "stable_fields": {
    "runtime_hash": "sha256hex",
    "last_event_hash": "sha256hex",
    "lineage_hash": "sha256hex",
    "contract_schema": "TANTRA_UNIGURU_INTELLIGENCE_CONTRACT_V1"
  },
  "verification_hash": "sha256hex"
}
```

---

## POST `/mitra/ecosystem/ask`

Governed, redacted Mitra interface. Returns only answer, trace, verification and evidence pointers. All internal governance payloads (`vijay_validation`, `gc_validation`, `mdu_validation`) are stripped.

### Request
Same as `/runtime/ecosystem/execute`.

### Response (200 OK)

```json
{
  "trace_id": "ecosystem_mitra_abc123",
  "answer": "string",
  "verification_status": "VERIFIED | NO_VERIFIED_KNOWLEDGE | PARTIAL_VERIFIED_SAMPLE",
  "confidence": 0.0,
  "decision": "answer | block",
  "replay_safe": true,
  "contract_schema": "TANTRA_UNIGURU_INTELLIGENCE_CONTRACT_V1",
  "downstream_consumable": true,
  "observability_state": "live_runtime_trace_complete",
  "evidence": {
    "ecosystem_proof": "review_packets/integration_proof/ecosystem_execution_latest.json",
    "bucket_proof": "review_packets/integration_proof/bucket_ecosystem_abc123.json"
  }
}
```

---

## GET `/health`

```json
{
  "status": "ok",
  "service": "uniguru-ecosystem-runtime",
  "schema_version": "UNIGURU_RUNTIME_RESPONSE_CONTRACT_V1",
  "capabilities": ["runtime_execute", "ecosystem_execute", "ecosystem_replay", "mitra_governed_ask"]
}
```

## GET `/ready`

```json
{
  "status": "ready",
  "proof_dir": "/path/to/review_packets/integration_proof",
  "masterdb_present": true
}
```

## GET `/metrics`

Prometheus-format text:
```
# HELP uniguru_ecosystem_runtime_info Ecosystem runtime capability metadata
# TYPE uniguru_ecosystem_runtime_info gauge
uniguru_ecosystem_runtime_info{service="uniguru",capability="bhiv_ecosystem"} 1
# HELP uniguru_ecosystem_runtime_ready Runtime readiness flag
# TYPE uniguru_ecosystem_runtime_ready gauge
uniguru_ecosystem_runtime_ready 1
```

---

## Environment Variables (Production Deployment)

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `UNIGURU_API_AUTH_REQUIRED` | No | `true` | Enable/disable bearer token auth |
| `UNIGURU_API_TOKEN` | If auth=true | — | Production bearer token |
| `UNIGURU_BUCKET_TELEMETRY_ENABLED` | No | `false` | Enable HTTP Bucket telemetry |
| `UNIGURU_BUCKET_TELEMETRY_ENDPOINT` | If bucket=true | — | Bucket collector URL |
| `UNIGURU_BUCKET_TELEMETRY_TOKEN` | If bucket=true | — | Bucket bearer token |
| `UNIGURU_HOST` | No | `0.0.0.0` | Bind address |
| `UNIGURU_PORT` | No | `8000` | Bind port |
