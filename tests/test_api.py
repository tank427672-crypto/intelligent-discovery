from pathlib import Path

from fastapi.testclient import TestClient

from intelligent_discovery.api import app, service
from intelligent_discovery.repository import SQLiteRepository


def test_api_closed_loop(tmp_path: Path) -> None:
    original = service.repository
    service.repository = SQLiteRepository(tmp_path / "api.db")
    client = TestClient(app)
    try:
        task = client.post("/tasks", json={"question": "AI 工具兼容性", "context": "旧设备"})
        task_id = task.json()["id"]
        source = client.post(
            f"/tasks/{task_id}/sources",
            json={
                "title": "官方资料",
                "url": "https://example.com/a",
                "excerpt": "要求 Apple Silicon",
                "credibility": 0.9,
                "source_type": "web",
                "trust_level": "primary",
                "status": "accessible",
                "license_info": "official terms",
            },
        )
        evidence = client.post(
            f"/tasks/{task_id}/evidence",
            json={
                "source_id": source.json()["id"],
                "claim": "要求 Apple Silicon",
                "excerpt": "要求 Apple Silicon",
                "locator": "hardware requirements",
            },
        )
        finding = client.post(
            f"/tasks/{task_id}/findings",
            json={
                "statement": "Intel 设备可能受限",
                "kind": "risk",
                "confidence": 0.8,
                "evidence_ids": [evidence.json()["id"]],
            },
        )
        feedback = client.post(
            f"/tasks/{task_id}/feedback",
            json={"finding_id": finding.json()["id"], "verdict": "needs_revision", "comment": "补充版本范围"},
        )
        assert [
            task.status_code,
            source.status_code,
            evidence.status_code,
            finding.status_code,
            feedback.status_code,
        ] == [
            201,
            201,
            201,
            201,
            201,
        ]
        assert client.post(f"/tasks/{task_id}/analyze").status_code == 200
        assert client.post(f"/tasks/{task_id}/complete").status_code == 201
        report = client.get(f"/tasks/{task_id}/report")
        assert "hardware requirements" in report.text
        assert "补充版本范围" in report.text
        assert client.get("/knowledge").json()[0]["title"] == "AI 工具兼容性"
    finally:
        service.repository = original
