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
