from __future__ import annotations

from integrations.mdu_client import MDUClient


class _FakeResponse:
    def __init__(self, body: str, status: int = 200) -> None:
        self._body = body.encode("utf-8")
        self.status = status

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_mdu_client_uses_canonical_dataset_lookup(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake_urlopen(req, timeout=5.0):
        calls.append((req.full_url, req.get_method()))
        return _FakeResponse('{"id": "dataset-123", "canonical_id": "BHIV-DS-DEMO-001"}')

    monkeypatch.setattr("integrations.mdu_client.urllib.request.urlopen", fake_urlopen)

    client = MDUClient()
    client.enabled = True
    client.base_url = "https://bhiv-mdu-api.onrender.com"

    result = client.validate_schema({"canonical_id": "BHIV-DS-DEMO-001"})

    assert result["live"] is True
    assert result["schema_compatible"] is True
    assert calls[0][0].endswith("/api/v1/datasets/canonical/BHIV-DS-DEMO-001")
    assert calls[0][1] == "GET"
