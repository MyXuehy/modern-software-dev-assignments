from __future__ import annotations

from typing import Annotated, Optional

from pydantic import BaseModel, StringConstraints


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ErrorResponse(BaseModel):
    detail: str


class NoteCreateRequest(BaseModel):
    content: NonEmptyString


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ExtractRequest(BaseModel):
    text: NonEmptyString
    save_note: bool = False


class ExtractedItem(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: Optional[int] = None
    items: list[ExtractedItem]


class ActionItemResponse(BaseModel):
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str


class MarkDoneRequest(BaseModel):
    done: bool = True


class MarkDoneResponse(BaseModel):
    id: int
    done: bool


