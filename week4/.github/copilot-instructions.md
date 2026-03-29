# Week4 Copilot Instructions（中文）

> 适用范围：`week4/` 目录。目标是高质量完成 P3，并支持后续 SubAgent 与 SQLite MCP 扩展。

## 1. 强制工作流

1. 先计划，再实现：先给出技术方案与文件改动清单，再写代码。
2. 先测后改：优先补/改测试，再做最小实现改动。
3. 改后回归：至少运行相关测试；涉及接口行为时做全量后端回归。
4. 输出必须简洁中文：优先给结论、风险、下一步，不贴大段无关代码。

## 2. P3（Complete action item flow）优先级与验收

### 2.1 优先级
- 优先处理 `PUT /action-items/{id}/complete` 的稳定性与边界行为。
- 保持错误信息英文（例如：`Action item not found`）。
- 仅做最小必要改动，避免引入与 P3 无关的功能扩展。

### 2.2 必过验收项
- `success`：存在的 action item 调用 complete 返回 `200`，且 `completed=true`。
- `not_found`：不存在 id 返回 `404`，错误信息为英文。
- `idempotent`：重复 complete 不反转状态，语义保持稳定。
- `list_reflect`：列表接口可观察到完成状态变化。

### 2.3 推荐测试文件
- `week4/backend/tests/test_action_items.py`
- `week4/backend/tests/conftest.py`

## 3. SubAgent 协作规范（可在 Copilot/Codex 里模拟）

### 3.1 角色职责
- `TestAgent`：只负责测试用例与断言，不改业务逻辑。
- `CodeAgent`：只负责最小实现改动，让测试通过。
- `ReviewAgent`：只负责审查风险、验收门（gates）与回归结论。

### 3.2 交接包（必须结构化）
每轮交接只传以下字段，避免上下文污染：
- `task_id`
- `goal`
- `changed_files`
- `failed_assertions`
- `open_risks`

### 3.3 验收门（Gates）
1. `Gate-Input`：参数与路径合法。
2. `Gate-Test`：相关测试通过。
3. `Gate-Idempotency`：重复执行不产生额外副作用。
4. `Gate-Safety`：无破坏性命令、无越权写操作。
5. `Gate-Output`：输出字段完整，可直接写入文档。

## 4. SQLite MCP 规范（Optional #3）

### 4.1 范围与路径
- 使用 SQLite MCP 做数据审计。
- 项目内配置文件：`week4/.claude/commands/mcp.json`。

### 4.2 安全规则
- 默认只读：仅允许 `SELECT`。
- 禁止 DML/DDL：`INSERT/UPDATE/DELETE/DROP/ALTER/CREATE`。
- 检测到写语句时，直接返回英文错误并停止执行。

### 4.3 示例查询（用于 writeup 证据）
```sql
SELECT COUNT(*) AS total,
       SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS done
FROM action_items;
```

```sql
SELECT id, description, completed
FROM action_items
ORDER BY id DESC
LIMIT 5;
```

## 5. 输出风格与文档要求

- 输出语言：中文。
- 风格：简洁、可执行、先结论后细节。
- 引用文件路径必须用反引号，例如：`week4/backend/tests/test_action_items.py`。
- 改动说明必须包含：
  - 改了什么（文件级）
  - 为什么改（风险/边界）
  - 如何验证（测试命令/结果）

## 6. 安全与防御性约束

- 禁止破坏性命令：`rm -rf`、`git reset --hard`、`git clean -fd`。
- 禁止吞异常：新增异常处理必须给出可诊断信息。
- 关键状态流转上方补充简短注释，说明“为什么这样做”。
- 若发现大范围非预期改动，必须先暂停并请求人工确认。

## 7. 推荐执行命令（Windows PowerShell）

```powershell
cd D:\code\Python\CS146S\week4
make test
```

```powershell
cd D:\code\Python\CS146S\week4
$env:PYTHONPATH='.'
pytest -q backend/tests/test_action_items.py
```

## 8. 单次任务输出模板

每次任务收尾时按以下结构输出：
- `status`: `passed|failed|blocked`
- `summary`: 一句话结论
- `artifacts`: 变更文件列表
- `risks`: 现存风险与潜在 bug 点
- `next_actions`: 下一步（最多 3 条）
