from __future__ import annotations

from typing import Annotated, Optional

from pydantic import BaseModel, StringConstraints


# 复用型字符串约束：自动去首尾空格，且不能为空。
NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ErrorResponse(BaseModel):
    # 统一错误响应格式，方便前端稳定处理。
    detail: str


class NoteCreateRequest(BaseModel):
    # 创建笔记时必须提供非空内容。
    content: NonEmptyString


class NoteResponse(BaseModel):
    # 单条笔记的标准返回结构。
    id: int
    content: str
    created_at: str


class ExtractRequest(BaseModel):
    # text 为待提取文本；save_note 控制是否把原文存入 notes 表。
    text: NonEmptyString
    save_note: bool = False


class ExtractedItem(BaseModel):
    # 每个提取结果都包含数据库 id 与文本。
    id: int
    text: str


class ExtractResponse(BaseModel):
    # 如果未保存原始 note，note_id 可能为 None。
    note_id: Optional[int] = None
    items: list[ExtractedItem]


class ActionItemResponse(BaseModel):
    # action item 查询接口返回的完整对象。
    id: int
    note_id: Optional[int] = None
    text: str
    done: bool
    created_at: str


class MarkDoneRequest(BaseModel):
    # done 默认为 True，表示“标记完成”。
    done: bool = True


class MarkDoneResponse(BaseModel):
    # 标记完成接口返回最小确认信息。
    id: int
    done: bool


