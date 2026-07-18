from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Dict

logger = logging.getLogger("uniguru.integrations.mdu_client")

# Canonical IDs registered in the live BHIV MDU registry
UNIGURU_CANONICAL_ID = "BHIV-DS-UNIGURU-RUNTIME-001"
UNIGURU_DATASET_ID = "dc02d460-8ee7-4643-88cb-8f891d991301"
UNIGURU_SCHEMA_ID = "37c845cb-0846-4e09-93b9-62b07655ad9f"

# Ecosystem canonical datasets owned by Vijay / InsightFlow Team
MDU_REPLAY_EVENTS_ID = "BHIV-DS-REPLAY-SEMANTIC-EVENTS-001"
MDU_LINEAGE_CHAIN_ID = "BHIV-DS-LINEAGE-CHAIN-001"
MDU_TRUST_PROPAGATION_ID = "BHIV-DS-TRUST-PROPAGATION-001"


class MDUClient:
    """
    Live client for the BHIV MDU (Master Data Universe) registry.

    Auth: X-API-Key header (not Bearer).
    Base URL: https://bhiv-mdu-api.onrender.com

    Confirmed working endpoints:
      GET  /api/v1/datasets                              — list all datasets
      GET  /api/v1/datasets/canonical/{canonical_id}    — lookup by canonical ID
      POST /api/v1/datasets/                             — register dataset
      POST /api/v1/schemas/                              — register schema
      GET  /api/v1/schemas/{schema_id}                  — get schema by ID
    """

    def __init__(self) -> None:
        self.enabled = os.getenv("MDU_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
        self.base_url = os.getenv("MDU_BASE_URL", "https://bhiv-mdu-api.onrender.com").strip().rstrip("/")
        self.api_key = os.getenv("MDU_API_KEY", "").strip()
        self.timeout = float(os.getenv("MDU_TIMEOUT_SECONDS", "10.0"))

    # ------------------------------------------------------------------
    # Schema validation — lookup UniGuru's registered schema
    # ------------------------------------------------------------------
    def validate_schema(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify UniGuru's schema is registered and active in MDU."""
        result = self._get(f"/api/v1/schemas/{UNIGURU_SCHEMA_ID}")
        result["canonical_id"] = UNIGURU_CANONICAL_ID
        result["dataset_id"] = UNIGURU_DATASET_ID
        result["schema_id"] = UNIGURU_SCHEMA_ID
        result["trace_id"] = payload.get("trace_id") or payload.get("evidence_id")
        return result

    # ------------------------------------------------------------------
    # Provenance validation — lookup UniGuru's canonical dataset
    # ------------------------------------------------------------------
    def validate_provenance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify UniGuru's dataset registration and provenance in MDU."""
        result = self._get(f"/api/v1/datasets/canonical/{UNIGURU_CANONICAL_ID}")
        result["trace_id"] = payload.get("trace_id")
        result["lineage_hash"] = payload.get("lineage_hash")
        result["runtime_hash"] = payload.get("runtime_hash")
        return result

    # ------------------------------------------------------------------
    # Replay lineage — verify ecosystem replay datasets are accessible
    # ------------------------------------------------------------------
    def validate_replay_lineage(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verify replay and lineage ecosystem datasets are active in MDU."""
        replay = self._get(f"/api/v1/datasets/canonical/{MDU_REPLAY_EVENTS_ID}")
        lineage = self._get(f"/api/v1/datasets/canonical/{MDU_LINEAGE_CHAIN_ID}")
        return {
            "live": replay.get("live", False) and lineage.get("live", False),
            "trace_id": payload.get("trace_id"),
            "replay_dataset": replay,
            "lineage_dataset": lineage,
            "replay_compatible": replay.get("data", {}).get("replay_compatibility") == "FULL"
                if replay.get("live") else False,
        }

    # ------------------------------------------------------------------
    # Internal HTTP helpers
    # ------------------------------------------------------------------
    def _get(self, path: str) -> Dict[str, Any]:
        if not self.enabled or not self.api_key:
            return {"live": False, "reason": "not_configured", "path": path}
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = {"X-API-Key": self.api_key, "Accept": "application/json"}
        req = urllib.request.Request(url=url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body) if body.strip() else {}
                return {"live": True, "status": resp.status, "data": data, "path": path}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            logger.warning("MDU GET %s failed %s: %s", path, exc.code, body[:200])
            return {"live": False, "status": exc.code, "reason": body[:200], "path": path}
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("MDU GET %s failed: %s", path, exc)
            return {"live": False, "reason": str(exc), "path": path}

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or not self.api_key:
            return {"live": False, "reason": "not_configured", "path": path}
        url = f"{self.base_url}{path}"
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        headers: Dict[str, str] = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        req = urllib.request.Request(url=url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body) if body.strip() else {}
                return {"live": True, "status": resp.status, "data": data, "path": path}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            logger.warning("MDU POST %s failed %s: %s", path, exc.code, body[:200])
            return {"live": False, "status": exc.code, "reason": body[:200], "path": path}
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("MDU POST %s failed: %s", path, exc)
            return {"live": False, "reason": str(exc), "path": path}

    def is_live(self) -> bool:
        return self.enabled and bool(self.api_key)
