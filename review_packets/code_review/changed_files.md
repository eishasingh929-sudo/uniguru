# Changed Files Inventory
## UniGuru BHIV Ecosystem Integration

**Sprint:** Production Convergence (Phase 1–3)
**Generated:** 2026-07-10

---

## Files Added This Sprint

| File | Purpose | Role in Integration |
|------|---------|---------------------|
| `backend/service/ecosystem_runtime.py` | BHIV ecosystem orchestrator | **Critical path** – composes all 7 integration touchpoints |
| `backend/service/uniguru_runtime_api.py` | FastAPI app with ecosystem endpoints | **Critical path** – exposes `/runtime/ecosystem/execute`, `/runtime/ecosystem/replay`, `/mitra/ecosystem/ask` |
| `backend/tests/test_ecosystem_integration.py` | Ecosystem integration tests | Verifies all 3 ecosystem endpoints |
| `scripts/run_ecosystem_acceptance.py` | End-to-end acceptance runner | Generates all `review_packets/` artefacts |
| `scripts/run_fault_injection.py` | Resilience validation | Tests empty/oversized queries, out-of-domain, replay determinism, concurrency |
| `scripts/run_stability_validation.py` | Long-duration validation | 30-query stability sweep with latency drift analysis |
| `review_packets/code_review/` (this folder) | Reviewer documentation | Full code review packet |

---

## Files Modified This Sprint

| File | Change | Reason |
|------|--------|--------|
| `backend/service/uniguru_runtime_api.py` | Added `field_validator` to `EcosystemRuntimeRequest` | Reject whitespace-only queries with 422 (resilience hardening) |

---

## Files Unchanged (referenced in integration, not modified)

| File | Role |
|------|------|
| `backend/governance/constitutional_runtime.py` | Vijay replay validation engine – called by `ecosystem_runtime.py` |
| `backend/kosha/deterministic_pipeline.py` | Kosha deterministic pipeline – single canonical retrieval path |
| `backend/memory/constitutional_semantic_memory.py` | `stable_hash()` function – replay-safe hashing |
| `backend/integrations/bucket_telemetry.py` | Bucket telemetry client (file-backed in local validation) |
| `backend/contracts/runtime_evidence_contract.json` | MDU schema contract – required fields for provenance validation |
| `backend/memory/constitutional_semantic_memory.py` | Deterministic hashing, UTC timestamps |

---

## Artefacts Generated

| Artefact | Location |
|----------|----------|
| Ecosystem execution proof | `review_packets/integration_proof/ecosystem_execution_latest.json` |
| Replay verification proof | `review_packets/integration_proof/replay_verification_latest.json` |
| Bucket telemetry proof | `review_packets/integration_proof/bucket_ecosystem_acceptance_live.json` |
| Acceptance report | `review_packets/validation_reports/ecosystem_acceptance_report.json` |
| Benchmark report | `review_packets/proof_logs/benchmark_report.json` |
| Fault injection report | `review_packets/proof_logs/fault_injection_report.json` |
| Stability report | `review_packets/proof_logs/stability_report.json` |
| Deployment validation | `review_packets/deployment_proof/ecosystem_deployment_validation.json` |
| API response logs | `review_packets/logs/ecosystem_acceptance_api_responses.json` |
