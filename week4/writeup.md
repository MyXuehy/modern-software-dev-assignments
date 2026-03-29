# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **Claude Code best practices (anthropic.com/engineering/claude-code-best-practices); SubAgents overview (docs.anthropic.com/en/docs/claude-code/sub-agents)**

This assignment took me about **2** hours to do.


## YOUR RESPONSES
### Automation #1
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> 参考 Claude Code best practices（参数化、可重复执行、默认安全）和 SubAgents overview（角色分工+上下文隔离）。我把 P3 高频流程做成命令模板，目标是让每次改动都走同一条可审计路径。

b. Design of each automation, including goals, inputs/outputs, steps
> 文件：`week4/.claude/commands/p3-complete-flow.md`
> 目标：围绕 P3 执行“测试优先 -> 最小实现 -> 回归验证 -> 摘要输出”。
> 输入：`scope`、`test_target`、`strict404`。
> 输出：`status/summary/artifacts/risks/next_actions`。
> 步骤：先跑定向测试 -> 补 404 与幂等测试 -> 必要时最小修正代码 -> 回归测试。

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> 在当前 Copilot/Codex 工作流中，打开 `p3-complete-flow.md`，填参数后作为提示词执行。
> 期望输出：
> - 变更文件列表
> - P3 测试结论
> - 若失败，给出最小修复建议
>
> 验证命令（PowerShell）：
> ```powershell
> cd D:\code\Python\CS146S\week4
> pytest -q backend/tests/test_action_items.py
> pytest -q backend/tests
> ```
> 安全/回滚：禁止破坏性命令（如 `git reset --hard`）；若回归失败，回滚最近一次相关变更。

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before：每次手动决定先改代码还是先写测试，路径不固定，容易漏 404/幂等边界。
> After：固定为“先测试后实现”的单路径流程，输出结构统一，可快速复盘。

e. How you used the automation to enhance the starter application
> 我用该自动化补齐了 P3 的边界测试：`404 not found`、重复 complete 幂等、列表状态反映完成态，确保 `PUT /action-items/{id}/complete` 的行为可验证且稳定。


### Automation #2
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> 参考 best practices 的“自动化可观察性”，把 writeup 证据抽成可重复生成模板；同时保留可迁移到 Claude slash command 的参数接口。

b. Design of each automation, including goals, inputs/outputs, steps
> 文件：`week4/.claude/commands/writeup-sql-proof.md`
> 目标：自动产出 writeup 需要的 SQL 证据片段。
> 输入：`db_path`、`queries`、`output_section`。
> 输出：SQL 输入、示例结果、可粘贴 markdown。
> 步骤：校验 DB 路径 -> 执行只读 SQL -> 格式化为 writeup 段落。

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> 在当前 Copilot/Codex 工作流中，打开 `writeup-sql-proof.md` 作为提示模板执行。
> 本地验证 SQL（PowerShell + sqlite3，若本机已安装 sqlite3）：
> ```powershell
> cd D:\code\Python\CS146S\week4
> sqlite3 data/app.db "SELECT COUNT(*) AS total, SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS done FROM action_items;"
> sqlite3 data/app.db "SELECT id, description, completed FROM action_items ORDER BY id DESC LIMIT 5;"
> ```
> 期望输出：可直接贴到 writeup 的表格/结构化结果。
> 安全/回滚：仅允许 `SELECT`，拒绝 DML/DDL，避免误写数据库。

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before：writeup 证据临时手写，格式不一致。
> After：SQL 证据可重复生成，结构统一，可直接粘贴。

e. How you used the automation to enhance the starter application
> 我用它验证了 P3 完成流在数据库中的持久化状态，并把查询与结果写入文档，减少主观描述。


### *(Optional) Automation #3*
*If you choose to build additional automations, feel free to detail them here!*

a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> 参考 SubAgents 文档中的“职责边界”，我增加了 SQLite MCP 查询模板，专注只读审计，不参与业务写入。

b. Design of each automation, including goals, inputs/outputs, steps
> 文件：`week4/.claude/commands/sqlite-mcp-query.md` + `week4/.claude/commands/mcp.json`。
> 目标：通过 SQLite MCP 快速审计 action item 状态。
> 输入：`query`、`limit`、`format`。
> 输出：`query_meta/rows_preview/row_count`。
> 步骤：加载 MCP 配置 -> 执行只读查询 -> 返回结构化结果。

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> 你手动接入 `mcp.json` 后，按 `sqlite-mcp-query.md` 传入查询即可。
> 示例 SQL：
> ```sql
> SELECT id, description, completed
> FROM action_items
> ORDER BY id DESC
> LIMIT 5;
> ```
> 示例结果（sample）：
> | id | description | completed |
> |---:|---|---:|
> | 7 | Ship it | 1 |
> | 6 | Write tests | 0 |
>
> 安全/回滚：默认只读；检测到写操作语句直接拒绝。

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> Before：需要手动打开 DB 做零散核验。
> After：通过固定模板快速查询并沉淀到 writeup 证据链。

e. How you used the automation to enhance the starter application
> 我用 Optional #3 辅助验证 P3 的完成态是否正确落盘，并用于展示“自动化驱动的数据校验”流程。
