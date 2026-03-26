from __future__ import annotations

import os
import re
import json
from typing import Any, List

from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)

DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
LLM_SYSTEM_PROMPT = (
    "You extract actionable tasks from meeting notes. "
    "Return only a JSON array of strings. "
    "Do not include explanations, markdown, or extra keys."
)


def _is_action_line(line: str) -> bool:
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


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
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


def extract_action_items_llm(text: str) -> List[str]:
    if not text or not text.strip():
        return []

    model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    schema: dict[str, Any] = {"type": "array", "items": {"type": "string"}}

    try:
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
            return _dedupe_items(parsed)
        return []
    except Exception:
        # Keep behavior resilient when Ollama is unavailable or returns invalid output.
        return extract_action_items(text)


def _looks_imperative(sentence: str) -> bool:
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


def _parse_llm_items(raw: str) -> List[str]:
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, list):
        return [item.strip() for item in data if isinstance(item, str) and item.strip()]
    if isinstance(data, dict):
        for key in ("action_items", "items"):
            candidate = data.get(key)
            if isinstance(candidate, list):
                return [item.strip() for item in candidate if isinstance(item, str) and item.strip()]
    return []


def _dedupe_items(items: List[str]) -> List[str]:
    # Deduplicate while preserving order.
    seen: set[str] = set()
    unique: List[str] = []
    for item in items:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique

