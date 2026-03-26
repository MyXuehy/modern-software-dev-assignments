from __future__ import annotations

from fastapi import APIRouter

from .. import db
from ..errors import NotFoundError
from ..schemas import NoteCreateRequest, NoteResponse


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse, status_code=201)
def create_note(payload: NoteCreateRequest) -> NoteResponse:
    note_id = db.insert_note(payload.content)
    note = db.get_note(note_id)
    if note is None:
        raise NotFoundError("note not found")
    return NoteResponse(**note)


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    row = db.get_note(note_id)
    if row is None:
        raise NotFoundError("note not found")
    return NoteResponse(**row)


