def _create_item(client, description: str = "Ship it") -> dict:
    r = client.post("/action-items/", json={"description": description})
    assert r.status_code == 201, r.text
    return r.json()


def test_complete_action_item_success(client):
    item = _create_item(client)
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200, r.text
    done = r.json()
    assert done["id"] == item["id"]
    assert done["completed"] is True


def test_complete_action_item_not_found(client):
    r = client.put("/action-items/999999/complete")
    assert r.status_code == 404
    assert r.json()["detail"] == "Action item not found"


def test_complete_action_item_idempotent(client):
    item = _create_item(client, description="Repeat completion")

    first = client.put(f"/action-items/{item['id']}/complete")
    assert first.status_code == 200, first.text
    assert first.json()["completed"] is True

    second = client.put(f"/action-items/{item['id']}/complete")
    assert second.status_code == 200, second.text
    assert second.json()["completed"] is True


def test_list_reflects_completed_state(client):
    item = _create_item(client, description="List should show done")

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200, r.text

    r = client.get("/action-items/")
    assert r.status_code == 200, r.text
    items = r.json()
    match = next((entry for entry in items if entry["id"] == item["id"]), None)
    assert match is not None
    assert match["completed"] is True
