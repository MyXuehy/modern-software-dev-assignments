import re

TAG_PATTERN = re.compile(r"(?<!\w)#([A-Za-z0-9_-]+)")
EXCLAMATION_ACTION_PATTERN = re.compile(r"!\s*(?:#[A-Za-z0-9_-]+\s*)*$")


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(value)
    return unique


def extract_action_items(text: str, include_tags: bool = False) -> list[str] | dict[str, list[str]]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    items = [
        line
        for line in lines
        if EXCLAMATION_ACTION_PATTERN.search(line) or line.lower().startswith("todo:")
    ]
    items = _dedupe(items)

    if not include_tags:
        return items

    # Keep leading '#' so callers can render tags directly without reformatting.
    tags = [f"#{match}" for match in TAG_PATTERN.findall(text)]
    return {"items": items, "tags": _dedupe(tags)}
