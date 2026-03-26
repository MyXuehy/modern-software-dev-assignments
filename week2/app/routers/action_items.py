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
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    # 保留原有提取入口：使用规则法，便于和 LLM 结果对比。
    return _extract_with(payload, use_llm=False)


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    # TODO4 新增入口：专门调用 LLM 提取。
    return _extract_with(payload, use_llm=True)


def _extract_with(payload: ExtractRequest, use_llm: bool) -> ExtractResponse:
    text = payload.text
    note_id: Optional[int] = None
    if payload.save_note:
        # 可选：先保存原始笔记，再把提取出的 action item 关联到该 note。
        note_id = db.insert_note(text)

    items = extract_action_items_llm(text) if use_llm else extract_action_items(text)
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


