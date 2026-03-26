from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter

from .. import db
from ..errors import NotFoundError
from ..schemas import (
    ActionItemResponse,
    ExtractRequest,
    ExtractResponse,
    ExtractedItem,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    # 原接口路径保持不变，但内部改为调用 LLM 提取函数。
    # 这样前端无需改动即可享受新能力。
    text = payload.text
    note_id: Optional[int] = None
    if payload.save_note:
        # 可选：先保存原始笔记，再把提取出的 action item 关联到该 note。
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ExtractedItem(id=item_id, text=text_value) for item_id, text_value in zip(ids, items)],
    )


@router.get("", response_model=List[ActionItemResponse])
def list_all(note_id: Optional[int] = None) -> List[ActionItemResponse]:
    # 提供可选过滤：传 note_id 只看某条笔记对应的任务。
    rows = db.list_action_items(note_id=note_id)
    return [ActionItemResponse(**row) for row in rows]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    # 更新任务完成状态；若目标不存在，返回 404 而不是静默成功。
    updated = db.mark_action_item_done(action_item_id, payload.done)
    if not updated:
        raise NotFoundError("action item not found")
    return MarkDoneResponse(id=action_item_id, done=payload.done)


