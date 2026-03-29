# /sqlite-mcp-query (Optional #3)

目标：通过 SQLite MCP 做只读审计查询，用于验证 P3 数据状态并生成 writeup 证据。

## Inputs
- `query`（必填）
- `limit`（默认 `50`，最大 `200`）
- `format`：`table|json`（默认 `table`）

## Safety
- 仅允许 `SELECT`。
- 检测到 DML/DDL（`INSERT|UPDATE|DELETE|DROP|ALTER|CREATE`）时返回英文错误并停止。

## Stop Conditions
- MCP 未连接或 DB 路径无效时停止。
- SQL 语法错误时停止，并返回错误片段与修复提示。

## Output Schema
- `status`
- `query_meta`
- `rows_preview`
- `row_count`
- `warning_or_error`

## Example Query
```sql
SELECT id, description, completed
FROM action_items
ORDER BY id DESC
LIMIT 5;
```

## Example Result (table)
| id | description | completed |
|---:|---|---:|
| 7 | Ship it | 1 |
| 6 | Write tests | 0 |

## Copilot/Codex 使用方式
- 将本文件作为查询提示模板。
- 执行前先确认 `mcp.json` 中 sqlite server 路径指向 `week4/data/app.db`。
