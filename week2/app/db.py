from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

# 建表 SQL 单独抽出，便于维护与复用。
CREATE_NOTES_TABLE = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
"""

CREATE_ACTION_ITEMS_TABLE = """
CREATE TABLE IF NOT EXISTS action_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER,
    text TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (note_id) REFERENCES notes(id)
);
"""


def ensure_data_directory_exists() -> None:
    # SQLite 数据库文件放在 data 目录；首次运行时确保目录存在。
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    # 每次数据库操作都通过该函数获取连接，统一连接配置。
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    # 让查询结果支持 row["字段名"] 访问，提升可读性。
    connection.row_factory = sqlite3.Row
    # 开启外键约束，避免写入非法 note_id。
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    # 应用启动时调用：若表不存在则创建，存在则保持不变。
    ensure_data_directory_exists()
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(CREATE_NOTES_TABLE)
        cursor.execute(CREATE_ACTION_ITEMS_TABLE)
        connection.commit()


def insert_note(content: str) -> int:
    # 插入一条笔记并返回主键 id，供后续关联 action item。
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        connection.commit()
        return int(cursor.lastrowid)


def _to_note(row: sqlite3.Row) -> dict[str, Any]:
    # 将 sqlite.Row 转成普通 dict，减少上层对数据库实现的耦合。
    return {
        "id": int(row["id"]),
        "content": str(row["content"]),
        "created_at": str(row["created_at"]),
    }


def _to_action_item(row: sqlite3.Row) -> dict[str, Any]:
    # done 字段在库里是 0/1，这里统一转成 Python 布尔值 True/False。
    return {
        "id": int(row["id"]),
        "note_id": row["note_id"],
        "text": str(row["text"]),
        "done": bool(row["done"]),
        "created_at": str(row["created_at"]),
    }


def list_notes() -> list[dict[str, Any]]:
    # 按 id 倒序返回笔记列表（新数据在前）。
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        return [_to_note(row) for row in cursor.fetchall()]


def get_note(note_id: int) -> Optional[dict[str, Any]]:
    # 读取单条笔记；未找到时返回 None。
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cursor.fetchone()
        return _to_note(row) if row is not None else None


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:
    # 批量插入 action items，返回每条记录的数据库 id。
    with get_connection() as connection:
        cursor = connection.cursor()
        ids: list[int] = []
        for item in items:
            # 跳过空白任务，避免产生无意义数据。
            cleaned = item.strip()
            if not cleaned:
                continue
            cursor.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, cleaned),
            )
            ids.append(int(cursor.lastrowid))
        connection.commit()
        return ids


def list_action_items(note_id: Optional[int] = None) -> list[dict[str, Any]]:
    # 支持按 note_id 过滤；不传 note_id 则返回全部任务。
    with get_connection() as connection:
        cursor = connection.cursor()
        if note_id is None:
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            )
        else:
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return [_to_action_item(row) for row in cursor.fetchall()]


def mark_action_item_done(action_item_id: int, done: bool) -> bool:
    # 更新完成状态；返回是否更新成功（用于上层决定是否返回 404）。
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        connection.commit()
        return cursor.rowcount > 0


