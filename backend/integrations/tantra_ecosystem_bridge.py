from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("uniguru.integrations.tantra_ecosystem_bridge")

# Locate brhamnda_tantara_integration repository
BRHAMNDA_INTEGRATION_CANDIDATES = [
    Path(os.getenv("BRHAMNDA_TANTARA_INTEGRATION_PATH", "")),
    Path("C:/Users/Isha Singh/Downloads/brhamnda_tantara_integration-main_extracted/brhamnda_tantara_integration-main"),
    Path(__file__).resolve().parents[3] / "Downloads" / "brhamnda_tantara_integration-main_extracted" / "brhamnda_tantara_integration-main",
]

_integration_repo_path: Optional[Path] = None
for candidate in BRHAMNDA_INTEGRATION_CANDIDATES:
    if candidate and candidate.exists() and (candidate / "services").exists():
        _integration_repo_path = candidate
        break

if _integration_repo_path and str(_integration_repo_path) not in sys.path:
    sys.path.insert(0, str(_integration_repo_path))

# Dynamic / Fallback Imports of Canonical Integration Services
try:
    from contracts.schemas import GameplayEvent, CapabilityResponse
    from services.insight_flow import InsightFlowTelemetry
    from services.bucket_storage import BucketStorageIntegration
    from services.replay_service import ReplayEvidenceGeneration
    from services.prana_client import PRANATrustVerification
    from services.karma_client import KARMACapabilityConsumption
    from services.insight_core import InsightCoreIntegration
    from services.insight_bridge import InsightBridgeClient
    from adapters.brahmanda_adapter import BrahmandaRuntimeAdapter
    CANONICAL_INTEGRATION_AVAILABLE = True
except ImportError as exc:
    logger.warning("Failed to import canonical TANTRA integration services: %s", exc)
    CANONICAL_INTEGRATION_AVAILABLE = False


class UniGuruTantraAdapter:
    """
    Adapts UniGuru Educational / Curriculum Execution events to the canonical InsightBridge.
    Ensures core UniGuru reasoning is preserved while participating in TANTRA PRANA, KARMA,
    Replay, Bucket, and InsightFlow operational fabric.
    """

    def __init__(self, bridge_client: InsightBridgeClient) -> None:
        self.bridge = bridge_client

    def on_uniguru_query_event(
        self,
        event_type: str,
        query: str,
        trace_id: str,
        verification_status: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event_payload = {
            "query": query,
            "verification_status": verification_status,
            "system": "uniguru",
        }
        if payload:
            event_payload.update(payload)

        event = GameplayEvent(
            event_type=event_type,
            trace_id=trace_id,
            payload=event_payload,
        )

        response = self.bridge.ingest_event(event)
        return response if isinstance(response, dict) else {}


class TantraEcosystemFabric:
    """
    Container for the complete live canonical TANTRA Operational Fabric.
    """

    def __init__(self) -> None:
        self.available = CANONICAL_INTEGRATION_AVAILABLE
        if self.available:
            self.flow = InsightFlowTelemetry()
            self.bucket = BucketStorageIntegration()
            self.replay = ReplayEvidenceGeneration()
            self.prana = PRANATrustVerification()
            self.karma = KARMACapabilityConsumption()
            self.core = InsightCoreIntegration(
                flow=self.flow,
                bucket=self.bucket,
                replay=self.replay,
                prana=self.prana,
                karma=self.karma,
            )
            self.bridge = InsightBridgeClient(self.core)
            self.adapter = UniGuruTantraAdapter(self.bridge)
        else:
            self.flow = None
            self.bucket = None
            self.replay = None
            self.prana = None
            self.karma = None
            self.core = None
            self.bridge = None
            self.adapter = None

    def process_uniguru_event(
        self,
        query: str,
        trace_id: str,
        verification_status: str,
        event_type: str = "CURRICULUM_QUERY",
        extra_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.available or not self.adapter:
            return {
                "trace_id": trace_id,
                "status": "UNAVAILABLE",
                "prana_verified": False,
                "karma_intelligence": {},
                "reason": "canonical_integration_not_loaded",
            }

        return self.adapter.on_uniguru_query_event(
            event_type=event_type,
            query=query,
            trace_id=trace_id,
            verification_status=verification_status,
            payload=extra_payload,
        )


_fabric_instance: Optional[TantraEcosystemFabric] = None


def get_tantra_ecosystem_fabric() -> TantraEcosystemFabric:
    global _fabric_instance
    if _fabric_instance is None:
        _fabric_instance = TantraEcosystemFabric()
    return _fabric_instance
