from __future__ import annotations

from fastapi import APIRouter

from .. import db
from ..errors import NotFoundError
from ..schemas import NoteCreateRequest, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    # 1) 写入数据库 2) 回查完整记录（含 created_at）3) 返回统一 schema
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise NotFoundError("note not found")
    return NoteResponse(**note)


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    # 根据路径参数读取单条 note；不存在时返回 404。
    row = db.get_note(note_id)
    if row is None:
        raise NotFoundError("note not found")
    return NoteResponse(**row)


@router.get("", response_model=list[NoteResponse])
def list_all_notes() -> list[NoteResponse]:
    # TODO4 新增：返回全部笔记，便于前端展示历史记录。
    rows = db.list_notes()
    return [NoteResponse(**row) for row in rows]
