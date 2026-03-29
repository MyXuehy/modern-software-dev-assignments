# /writeup-sql-proof

目标：生成可直接粘贴到 `week4/writeup.md` 的 SQL 证据片段（查询 + 示例结果 + 一句话结论）。

## Inputs
- `db_path`: 默认 `week4/data/app.db`
- `output_section`: 默认 `Automation #2`
- `queries`: 默认两条
  1. `SELECT COUNT(*) AS total, SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS done FROM action_items;`
  2. `SELECT id, description, completed FROM action_items ORDER BY id DESC LIMIT 5;`

## Safety
- 仅允许 `SELECT`。
- 如果检测到 `INSERT|UPDATE|DELETE|DROP|ALTER|CREATE`，立即拒绝并返回英文错误。

## Stop Conditions
- 数据库文件不存在时停止并返回 `status=failed`。
- 任一 SQL 执行失败时停止并报告失败 SQL。

## Output Schema
- `status`
- `summary`
- `sql_inputs`
- `sample_results`
- `paste_ready_markdown`

## Paste-ready Template
```md
### SQL Evidence
Query 1:
```sql
SELECT COUNT(*) AS total, SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS done FROM action_items;
```
Result (sample):
| total | done |
|---:|---:|
| 3 | 2 |

Query 2:
```sql
SELECT id, description, completed FROM action_items ORDER BY id DESC LIMIT 5;
```
Result (sample):
| id | description | completed |
|---:|---|---:|
| 7 | Ship it | 1 |
| 6 | Write tests | 0 |

结论：P3 的 complete 流程在数据库层可验证，已完成项状态可稳定持久化。
```

## Idempotency
- 相同输入应生成同结构输出，便于重复粘贴与 diff。
