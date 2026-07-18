from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import Any, Dict

logger = logging.getLogger("uniguru.integrations.insightflow_client")


class InsightFlowClient:
    """
    Emits runtime traces, decision lineage, and execution metrics to InsightFlow.
    Env-gated; degrades gracefully when endpoint is not configured.
    """

    def __init__(self) -> None:
        self.enabled = os.getenv("INSIGHTFLOW_ENABLED", "false").strip().lower() in {"1", "true", "yes", "on"}
        self.base_url = os.getenv("INSIGHTFLOW_BASE_URL", "").strip().rstrip("/")
        self.token = os.getenv("INSIGHTFLOW_TOKEN", "").strip()
        self.timeout = float(os.getenv("INSIGHTFLOW_TIMEOUT_SECONDS", "3.0"))

    def emit_trace(self, trace_payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/traces", trace_payload)

    def emit_decision(self, decision_payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/decisions", decision_payload)

    def emit_metric(self, metric_payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/metrics", metric_payload)

    def emit_failure(self, failure_payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/failures", failure_payload)

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled or not self.base_url:
            return {"live": False, "reason": "not_configured", "path": path}
        url = f"{self.base_url}{path}"
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        headers: Dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = urllib.request.Request(url=url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                response_body = resp.read().decode("utf-8")
                data = json.loads(response_body) if response_body.strip() else {}
                return {"live": True, "status": resp.status, "data": data}
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning("InsightFlow call to %s failed: %s", path, exc)
            return {"live": False, "reason": str(exc), "path": path}

    def is_live(self) -> bool:
        return self.enabled and bool(self.base_url)
