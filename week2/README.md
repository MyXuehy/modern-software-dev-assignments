# Week 2 - Action Item Extractor

这是一个基于 FastAPI + SQLite 的小型应用：输入会议纪要或自由文本，提取可执行的 action items，并支持保存笔记、查看历史任务、标记任务完成。

## Project Overview

- 后端：`FastAPI`（见 `week2/app/main.py`）
- 数据库：`SQLite`（本地文件 `week2/data/app.db`，见 `week2/app/db.py`）
- 提取能力：
  - 规则提取：`extract_action_items()`
  - LLM 提取：`extract_action_items_llm()`（Ollama，失败时回退规则法）
- 前端：纯 HTML + 原生 JS（见 `week2/frontend/index.html`）

## Prerequisites

- Python（版本以仓库 `pyproject.toml` 为准）
- Poetry
- 可选：Ollama（仅在你要用 LLM 提取时需要）

## Setup and Run

1) 安装依赖（在仓库根目录执行）：

```powershell
cd D:\code\Python\CS146S
poetry install
```

2) 启动服务：

```powershell
cd D:\code\Python\CS146S
poetry run uvicorn week2.app.main:app --reload
```

3) 打开页面：

- App: http://127.0.0.1:8000/
- OpenAPI: http://127.0.0.1:8000/docs

## Optional: Ollama Setup (for LLM extraction)

`POST /action-items/extract-llm` 需要本地可用的 Ollama 模型。示例：

```powershell
ollama run llama3.2:3b
```

可通过环境变量覆盖模型名（默认是 `llama3.2:3b`）：

```powershell
$env:OLLAMA_MODEL = "llama3.2:3b"
```

## API Endpoints and Functionality

### Notes

- `POST /notes`
  - 创建一条笔记
  - Request: `{ "content": "..." }`
  - Response: `NoteResponse`
- `GET /notes/{note_id}`
  - 查询单条笔记，不存在返回 404
- `GET /notes`
  - 查询全部笔记（TODO4 新增）

### Action Items

- `POST /action-items/extract`
  - 使用规则法提取 action items
  - Request: `{ "text": "...", "save_note": true|false }`
  - Response: `ExtractResponse`
- `POST /action-items/extract-llm`
  - 使用 LLM 提取 action items（TODO4 新增）
  - Request/Response 与 `/extract` 相同
- `GET /action-items?note_id=<id>`
  - 获取任务列表；可按 note_id 过滤
- `POST /action-items/{action_item_id}/done`
  - 更新任务完成状态
  - Request: `{ "done": true|false }`
  - 不存在返回 404

> 详细请求/响应结构请参考 `week2/app/schemas.py`。

## Frontend Usage

前端页面（`/`）支持以下按钮：

- `Extract`：调用 `/action-items/extract`
- `Extract LLM`：调用 `/action-items/extract-llm`
- `List Notes`：调用 `/notes` 并展示历史笔记

## Running Tests

在仓库根目录执行：

```powershell
cd D:\code\Python\CS146S
poetry run pytest week2/tests -q
```

只运行提取相关测试：

```powershell
cd D:\code\Python\CS146S
poetry run pytest week2/tests/test_extract.py -q
```

## Notes on Data Persistence

- 数据持久化到 `week2/data/app.db`
- 服务启动时会自动初始化表（不存在则创建）
- 删除该文件后再次启动，数据库会重新创建
