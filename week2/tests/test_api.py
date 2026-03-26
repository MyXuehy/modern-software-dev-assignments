from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from ..app import db
from ..app.main import app
from ..app.services import extract as extract_service


def _client_with_temp_db(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setattr(db, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    return TestClient(app)


def test_create_note_validates_non_empty_content(tmp_path, monkeypatch):
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.post("/notes", json={"content": "   "})

    assert response.status_code == 422


def test_get_missing_note_returns_404(tmp_path, monkeypatch):
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.get("/notes/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "note not found"}


def test_extract_endpoint_returns_typed_payload(tmp_path, monkeypatch):
    def fake_chat(**kwargs):
        return SimpleNamespace(message=SimpleNamespace(content='["Set up database"]'))

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.post("/action-items/extract", json={"text": "- [ ] Set up database"})

    assert response.status_code == 200
    body = response.json()
    assert body["note_id"] is None
    assert len(body["items"]) == 1
    assert body["items"][0]["text"] == "Set up database"


def test_mark_done_returns_404_for_missing_item(tmp_path, monkeypatch):
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.post("/action-items/4242/done", json={"done": True})

    assert response.status_code == 404
    assert response.json() == {"detail": "action item not found"}

