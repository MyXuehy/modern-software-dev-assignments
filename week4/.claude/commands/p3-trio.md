# /p3-trio

目标：使用角色分工方式完成 P3 迭代，保持上下文清洁并设置验收门（gates）。

参考：
- Claude Code best practices: https://www.anthropic.com/engineering/claude-code-best-practices
- SubAgents overview: https://docs.anthropic.com/en/docs/claude-code/sub-agents

> 当前主要在 Copilot/Codex 使用：本文件作为“角色协作提示词模板”。

## Roles
- `TestAgent`: 只写/改测试与断言，不改业务逻辑。
- `CodeAgent`: 只改实现让测试通过。
- `ReviewAgent`: 只做 gate 审查与风险判定。

## Inputs
- `task_id`: 任务编号（必填）
- `scope`: `backend|frontend|full`（默认 `backend`）
- `max_rounds`: 最大迭代轮次（默认 `2`）

## Context Isolation
- 每个角色只接收“交接包”，不共享完整聊天历史。
- 每轮交接前清空上下文，只注入最新交接包。
- 交接包必须包含：`task_id`、`goal`、`changed_files`、`failed_assertions`、`open_risks`。

## Gates
1. `Gate-Input`: 参数合法、路径存在。
2. `Gate-Test`: 相关测试通过。
3. `Gate-Idempotency`: 重复执行不产生额外副作用。
4. `Gate-Safety`: 无 denylist 指令、SQL 仅只读。
5. `Gate-Output`: 输出字段完整，可直接写入 `writeup.md`。

## Workflow
1. `TestAgent` 先定义/补充用例（404、幂等等）。
2. `CodeAgent` 最小实现改动。
3. `ReviewAgent` 逐 gate 审核。
4. 失败则进入下一轮，直到达到 `max_rounds`。

## Output Schema
- `status`: `passed|failed|needs-human`
- `summary`
- `artifacts`
- `gate_results`
- `next_actions`

## Copilot/Codex 使用方式
- 将 `Roles + Gates + Workflow` 分段作为提示词。
- 每轮只粘贴对应角色段，避免上下文污染。
