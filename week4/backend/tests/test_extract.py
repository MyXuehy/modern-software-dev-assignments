from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_action_items_with_tags():
    text = """
    TODO: write tests #backend #P1
    - Ship it! #release
    Ignore line #backend
    """.strip()

    result = extract_action_items(text, include_tags=True)
    assert result["items"] == ["TODO: write tests #backend #P1", "Ship it! #release"]
    assert result["tags"] == ["#backend", "#P1", "#release"]
