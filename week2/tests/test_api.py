from __future__ import annotations

from types import SimpleNamespace

from fastapi.testclient import TestClient

from ..app import db
from ..app.main import app
from ..app.services import extract as extract_service


def _client_with_temp_db(tmp_path, monkeypatch) -> TestClient:
    # 将数据库路径指向 pytest 临时目录，避免污染真实数据文件。
    monkeypatch.setattr(db, "DATA_DIR", tmp_path)
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    return TestClient(app)


def test_create_note_validates_non_empty_content(tmp_path, monkeypatch):
    # Pydantic 非空约束应拦截纯空白字符串。
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.post("/notes", json={"content": "   "})

    assert response.status_code == 422


def test_get_missing_note_returns_404(tmp_path, monkeypatch):
    # 查询不存在资源时应返回 404 与统一错误格式。
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.get("/notes/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "note not found"}


def test_extract_llm_endpoint_returns_typed_payload(tmp_path, monkeypatch):
    # mock LLM，验证路由返回结构与 schema 对齐。
    def fake_chat(**kwargs):
        return SimpleNamespace(message=SimpleNamespace(content='["Set up database"]'))

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.post("/action-items/extract-llm", json={"text": "- [ ] Set up database"})

    assert response.status_code == 200
    body = response.json()
    assert body["note_id"] is None
    assert len(body["items"]) == 1
    assert body["items"][0]["text"] == "Set up database"


def test_list_notes_returns_saved_notes(tmp_path, monkeypatch):
    # TODO4: 新增 /notes 列表接口，应返回已保存的笔记。
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        create_res = client.post("/notes", json={"content": "Sprint planning notes"})
        assert create_res.status_code == 201

        list_res = client.get("/notes")

    assert list_res.status_code == 200
    payload = list_res.json()
    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["content"] == "Sprint planning notes"


def test_mark_done_returns_404_for_missing_item(tmp_path, monkeypatch):
    # 更新不存在的 action item，接口应显式返回 404。
    with _client_with_temp_db(tmp_path, monkeypatch) as client:
        response = client.post("/action-items/4242/done", json={"done": True})

    assert response.status_code == 404
    assert response.json() == {"detail": "action item not found"}
