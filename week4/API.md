# Week4 API

Base URL: `http://127.0.0.1:8000`

## Notes

### `GET /notes/`
- 返回全部 notes。
- `200 OK`
- 响应示例：
```json
[
  {"id": 1, "title": "Sprint", "content": "Plan release"}
]
```

### `POST /notes/`
- 创建 note。
- 请求体：
```json
{"title": "Sprint", "content": "Plan release"}
```
- 校验：`title`、`content` 去空白后最小长度为 1。
- `201 Created`
- 校验失败：`400 Bad Request`

### `GET /notes/search/?q=...`
- 按 `title` 或 `content` 搜索（大小写不敏感）。
- `q` 为空白字符串时返回 `400`。
- `200 OK`

### `GET /notes/{note_id}`
- 按 id 读取 note。
- `200 OK`
- 不存在：`404 Not Found`，`{"detail":"Note not found"}`

### `PUT /notes/{note_id}`
- 更新 note（全量更新 `title`/`content`）。
- 请求体：
```json
{"title": "Updated", "content": "Updated content"}
```
- `200 OK`
- 不存在：`404 Not Found`，`{"detail":"Note not found"}`
- 校验失败：`400 Bad Request`

### `DELETE /notes/{note_id}`
- 删除 note。
- `204 No Content`
- 不存在：`404 Not Found`，`{"detail":"Note not found"}`

## Action Items

### `GET /action-items/`
- 返回全部 action items。
- `200 OK`

### `POST /action-items/`
- 创建 action item。
- 请求体：
```json
{"description": "Ship it"}
```
- 校验：`description` 去空白后最小长度为 1。
- `201 Created`
- 校验失败：`400 Bad Request`

### `PUT /action-items/{item_id}/complete`
- 标记 action item 为完成。
- `200 OK`
- 不存在：`404 Not Found`，`{"detail":"Action item not found"}`

## 其它

### `GET /`
- 返回前端页面 `frontend/index.html`。
- `200 OK`

## OpenAPI Drift Check
- 已与应用当前 OpenAPI 路由清单对齐：
  - `/`
  - `/notes/`
  - `/notes/search/`
  - `/notes/{note_id}`
  - `/action-items/`
  - `/action-items/{item_id}/complete`
