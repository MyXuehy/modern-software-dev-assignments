from types import SimpleNamespace

from ..app.services import extract as extract_service
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    # 规则提取器基础测试：覆盖 bullet、checkbox、有序列表。
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
    # 通过 monkeypatch 替换真实 Ollama 调用，保证单测不依赖外部服务。
    text = """
    Notes:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    """.strip()

    calls = []

    def fake_chat(**kwargs):
        # 模拟 LLM 返回结构化 JSON 字符串。
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
    # 断言调用参数包含结构化输出 schema 与低温度配置。
    assert calls[0]["format"] == {"type": "array", "items": {"type": "string"}}
    assert calls[0]["options"] == {"temperature": 0}


def test_extract_action_items_llm_keyword_lines(monkeypatch):
    # 覆盖 TODO/ACTION/NEXT 这类会议纪要常见前缀。
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
    # 空输入应直接返回 []，且不触发任何模型调用。
    def fail_chat(**kwargs):
        raise AssertionError("chat should not be called for empty input")

    monkeypatch.setattr(extract_service, "chat", fail_chat)

    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   \n  ") == []


def test_extract_action_items_llm_falls_back_on_chat_error(monkeypatch):
    # 当模型不可用时，函数应自动降级到规则提取器。
    text = "TODO: Write docs\nRandom sentence"

    def raise_chat(**kwargs):
        raise RuntimeError("Ollama unavailable")

    monkeypatch.setattr(extract_service, "chat", raise_chat)

    items = extract_action_items_llm(text)

    # Fallback should use heuristic extractor and still return a task.
    assert items == ["TODO: Write docs"]
