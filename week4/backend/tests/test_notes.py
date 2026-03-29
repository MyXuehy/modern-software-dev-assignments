def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_update_note_success(client):
    created = client.post("/notes/", json={"title": "Old", "content": "Before"})
    assert created.status_code == 201, created.text
    note_id = created.json()["id"]

    updated_payload = {"title": "New", "content": "After"}
    r = client.put(f"/notes/{note_id}", json=updated_payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["title"] == "New"
    assert body["content"] == "After"

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "New"


def test_update_note_not_found(client):
    r = client.put("/notes/999999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_delete_note_success(client):
    created = client.post("/notes/", json={"title": "Delete", "content": "Me"})
    assert created.status_code == 201, created.text
    note_id = created.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204, r.text

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_create_note_validation_failure_returns_400(client):
    r = client.post("/notes/", json={"title": "   ", "content": "Hello"})
    assert r.status_code == 400
    assert "title" in r.json()["detail"]


def test_update_note_validation_failure_returns_400(client):
    created = client.post("/notes/", json={"title": "T", "content": "C"})
    assert created.status_code == 201, created.text
    note_id = created.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Updated", "content": "   "})
    assert r.status_code == 400
    assert "content" in r.json()["detail"]


def test_search_notes_empty_query_returns_400(client):
    r = client.get("/notes/search/", params={"q": "   "})
    assert r.status_code == 400
    assert r.json()["detail"] == "Search query cannot be empty"


def test_search_notes_case_insensitive(client):
    created = client.post(
        "/notes/",
        json={"title": "Deploy Plan", "content": "Review Release Checklist"},
    )
    assert created.status_code == 201, created.text
    note_id = created.json()["id"]

    r = client.get("/notes/search/", params={"q": "deploy"})
    assert r.status_code == 200, r.text
    assert any(note["id"] == note_id for note in r.json())

    r = client.get("/notes/search/", params={"q": "RELEASE"})
    assert r.status_code == 200, r.text
    assert any(note["id"] == note_id for note in r.json())
