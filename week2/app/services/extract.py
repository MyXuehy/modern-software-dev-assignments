from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from ollama import chat

load_dotenv()

# 识别无序列表/有序列表前缀（例如 "- xxx"、"* xxx"、"1. xxx"）
BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)

# 默认模型可通过环境变量 OLLAMA_MODEL 覆盖，便于不同机器按性能调整。
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
# System Prompt 强约束输出格式：只返回 JSON 字符串数组。
LLM_SYSTEM_PROMPT = (
    "You extract actionable tasks from meeting notes. "
    "Return only a JSON array of strings. "
    "Do not include explanations, markdown, or extra keys."
)


def _is_action_line(line: str) -> bool:
    # 基于规则判断当前行是否“像任务”：
    # - 列表项
    # - 关键字前缀（TODO/ACTION/NEXT）
    # - 包含待办标记 [ ] / [todo]
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> list[str]:
    # 规则版提取器：速度快、可解释性强，但泛化能力有限。
    lines = text.splitlines()
    extracted: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    return _dedupe_items(extracted)


def extract_action_items_llm(text: str) -> list[str]:
    # LLM 版提取器：对复杂自然语言更鲁棒。
    if not text or not text.strip():
        # 空输入直接返回空列表，避免无意义模型调用。
        return []

    model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    schema: dict[str, Any] = {"type": "array", "items": {"type": "string"}}

    try:
        # 使用 Ollama chat，并通过 format schema 要求结构化输出。
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            format=schema,
            options={"temperature": 0},
        )
        content = response.message.content if getattr(response, "message", None) else ""
        parsed = _parse_llm_items(content)
        if parsed:
            # 统一去重，保证输出稳定。
            return _dedupe_items(parsed)
        return []
    except Exception:
        # Keep behavior resilient when Ollama is unavailable or returns invalid output.
        # 如果本地模型未启动/超时/格式异常，回退到规则版，保证接口可用。
        return extract_action_items(text)


def _looks_imperative(sentence: str) -> bool:
    # 简单判断句子是否像“祈使句任务”（例如 "Write tests"）。
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


def _parse_llm_items(raw: str) -> list[str]:
    # 将模型文本解析成 Python 列表，并做类型/空值清洗。
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, list):
        return [item.strip() for item in data if isinstance(item, str) and item.strip()]
    if isinstance(data, dict):
        # 兼容模型偶尔返回对象包裹的情况。
        for key in ("action_items", "items"):
            candidate = data.get(key)
            if isinstance(candidate, list):
                return [
                    item.strip() for item in candidate if isinstance(item, str) and item.strip()
                ]
    return []


def _dedupe_items(items: list[str]) -> list[str]:
    # Deduplicate while preserving order.
    # 使用小写键去重，避免同一任务因大小写不同重复出现。
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique
