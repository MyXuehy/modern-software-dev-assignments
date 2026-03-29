# Week4 技术方案（P3 + 自动化 + Optional SQLite MCP）

## 0. 目标与约束
- 主线任务：`P3 Complete action item flow`（`PUT /action-items/{id}/complete`）做最小增强。
- 自动化策略：先做简单自动化，再扩展 SubAgent 协作与 MCP。
- 交付目录：`week4/.claude/commands/`。
- 工具现实：当前使用 Codex + GitHub Copilot，不依赖 Claude Code 运行时。
- MCP 范围：仅 SQLite MCP，配置文件由我输出 `mcp.json`，你手动接入。
- 文案要求：错误信息保持英文；提交说明中文。
- 时限：总实施控制在 2h 内。
- Optional：SQLite MCP 作为 `writeup.md` 的 Optional #3。

## 1. 范围（Scope）
### 1.1 必做自动化（2个）
1. `p3-complete-flow.md`
   - 目标：把 P3 的测试、实现校验、结果摘要变成一次性流程。
2. `writeup-sql-proof.md`
   - 目标：生成 `writeup.md` 需要的 SQL 证据（SQL + 示例结果）。

### 1.2 扩展自动化（可迁移 SubAgent）
- 使用文档化的角色协作模板（Test/API/UI），在当前 Copilot/Codex 下以“提示词指导文件”方式运行。

### 1.3 Optional #3
- `sqlite-mcp-query.md` + `mcp.json`（SQLite only，项目内配置）。

## 2. 非目标（Non-Goals）
- 不接入除 SQLite 以外的 MCP。
- 不扩展到 P3 以外的大功能开发（如 Notes 全量 CRUD 重构）。
- 不引入新的前端构建链路或复杂基础设施。

## 3. 交付清单（Deliverables）
- `week4/.claude/commands/p3-complete-flow.md`
- `week4/.claude/commands/writeup-sql-proof.md`
- `week4/.claude/commands/p3-trio.md`（SubAgent 协作入口文档）
- `week4/.claude/commands/sqlite-mcp-query.md`（Optional #3）
- `week4/.claude/commands/mcp.json`（仅配置文件）
- `week4/writeup.md`（中文补全，含 SQL 示例结果）
- P3 对应最小测试增强（`backend/tests/test_action_items.py`）

## 4. P3 最小增强设计

### 4.1 后端行为
- 保持 `PUT /action-items/{id}/complete` 语义：
  - 目标存在：返回 `200` + `completed=true`。
  - 目标不存在：返回 `404` + 英文错误信息（`Action item not found`）。
- 重复 complete 建议保持幂等：再次调用仍返回 `200`，状态不反转。

### 4.2 前端行为
- 完成后该项展示为 `done`；不再出现可点击 `Complete` 按钮。

### 4.3 测试清单
1. `test_complete_action_item_success`
2. `test_complete_action_item_not_found`
3. `test_complete_action_item_idempotent`
4. `test_list_reflects_completed_state`

## 5. 自动化设计（I/O）

### 5.0 通用命令规范（Best Practices 对齐）
- 每个命令文档必须显式声明：`Inputs`、`Defaults`、`Invalid Input Handling`、`Stop Conditions`、`Output Schema`。
- 默认只读优先；任何写操作都要在文档中标注并可显式关闭。
- 命令必须可重复执行（幂等）：同输入重复运行时不产生额外副作用。
- 安全 denylist：禁止 `rm -rf`、`git reset --hard`、`git clean -fd`、非必要数据库写入语句。
- 输出固定字段：`status`、`summary`、`artifacts`、`risks`、`next_actions`。

### 5.1 `p3-complete-flow`
- 输入：`scope=backend|frontend|full`、`test_target`、`strict404=true|false`。
- 输出：
  - 变更文件清单
  - 测试结果摘要
  - 失败时的下一步修复建议
- 安全策略：只执行 lint/test/read 操作，避免破坏性命令。

### 5.2 `writeup-sql-proof`
- 输入：`db_path`、`queries`、`output_section`。
- 输出：可直接粘贴到 `writeup.md` 的 SQL 片段与示例结果。
- 示例 SQL（用于 writeup）：
  - `SELECT COUNT(*) AS total, SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) AS done FROM action_items;`
  - `SELECT id, description, completed FROM action_items ORDER BY id DESC LIMIT 5;`

### 5.3 `sqlite-mcp-query`（Optional #3）
- 输入：`query`、`limit`、`format=table|json`。
- 输出：查询结果或英文错误提示（路径/SQL 错误）。
- 限制：默认只读查询，检测到 DML/DDL 直接拒绝并返回英文错误。

## 6. 实施步骤（按顺序）
1. 先落 `SPEC.md`（当前文件）。
2. 新建 `week4/.claude/commands/` 下的 4 个命令文档。
3. 补齐 P3 最小测试与必要实现修正。
4. 输出 `mcp.json`（SQLite MCP，仅文件交付）。
5. 更新 `week4/writeup.md`（中文 + SQL 示例结果）。
6. 运行测试与静态检查，整理中文提交说明。

## 7. 验收标准
- P3 测试通过且新增边界测试覆盖到 404 + 幂等。
- 自动化文档可直接在当前工具链下作为提示词执行。
- `writeup.md` 含 SQL 示例输入与输出结果。
- Optional #3 在文档与配置文件层面交付完整。
- 四个命令文档均包含：1 个成功样例、1 个失败样例、1 个重复执行样例。
- SubAgent 协作文档提供 gates：输入门、测试门、幂等门、安全门、输出门。

## 8. 风险与回滚
- 风险：SQLite MCP 启动命令因本地环境差异失败。
  - 处理：仅交付 `mcp.json` 模板 + 命令文档，不耦合本地执行。
- 风险：P3 调整引发回归。
  - 处理：测试先行，小步修改，失败即回滚到前一提交。

## 9. 时间切片（2h）
- 0-20min：命令文档骨架（P3 + writeup）
- 20-55min：P3 测试增强与必要实现修正
- 55-85min：SubAgent 协作文档 + Optional #3 文档
- 85-105min：`mcp.json` + `writeup.md` SQL 示例
- 105-120min：测试回归、lint、中文提交说明
