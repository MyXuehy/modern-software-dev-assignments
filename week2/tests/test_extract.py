from types import SimpleNamespace

from ..app.services import extract as extract_service
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_bullets(monkeypatch):
    text = """
    Notes:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    """.strip()

    calls = []

    def fake_chat(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            message=SimpleNamespace(
                content='["Set up database", "implement API extract endpoint", "Write tests"]'
            )
        )

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    items = extract_action_items_llm(text)

    assert items == ["Set up database", "implement API extract endpoint", "Write tests"]
    assert len(calls) == 1
    assert calls[0]["format"] == {"type": "array", "items": {"type": "string"}}
    assert calls[0]["options"] == {"temperature": 0}


def test_extract_action_items_llm_keyword_lines(monkeypatch):
    text = """
    TODO: finalize sprint plan
    ACTION: call vendor
    NEXT: prepare demo
    """.strip()

    def fake_chat(**kwargs):
        return SimpleNamespace(
            message=SimpleNamespace(
                content='["finalize sprint plan", "call vendor", "prepare demo"]'
            )
        )

    monkeypatch.setattr(extract_service, "chat", fake_chat)

    items = extract_action_items_llm(text)

    assert items == ["finalize sprint plan", "call vendor", "prepare demo"]


def test_extract_action_items_llm_empty_input_does_not_call_chat(monkeypatch):
    def fail_chat(**kwargs):
        raise AssertionError("chat should not be called for empty input")

    monkeypatch.setattr(extract_service, "chat", fail_chat)

    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   \n  ") == []


def test_extract_action_items_llm_falls_back_on_chat_error(monkeypatch):
    text = "TODO: Write docs\nRandom sentence"

    def raise_chat(**kwargs):
        raise RuntimeError("Ollama unavailable")

    monkeypatch.setattr(extract_service, "chat", raise_chat)

    items = extract_action_items_llm(text)

    # Fallback should use heuristic extractor and still return a task.
    assert items == ["TODO: Write docs"]

