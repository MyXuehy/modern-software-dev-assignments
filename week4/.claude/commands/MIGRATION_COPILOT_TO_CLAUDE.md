# Copilot/Codex -> Claude 命令迁移说明

目标：当前在 Copilot/Codex 下先以“文档提示词”运行，后续可平滑迁移到 Claude slash command。

## 当前方式（Copilot/Codex）
1. 打开目标命令文档（如 `p3-complete-flow.md`）。
2. 填入参数（`scope/test_target/...`）。
3. 将 `Inputs + Workflow + Output Schema` 作为提示词执行。

## 迁移方式（Claude）
- 文件位置保持 `.claude/commands/*.md`。
- 命令名即文件名（如 `/p3-complete-flow`、`/p3-trio`）。
- 参数通过 `$ARGUMENTS` 传入。

## 兼容原则
- 文档先定义：输入、默认值、失败处理、停止条件、输出 schema。
- 每个命令都必须可幂等重复执行。
- 所有高风险操作默认禁用并显式提示。

## 最小验证清单
- 同命令重复执行两次，第二次不应新增副作用。
- 输出字段完整：`status/summary/artifacts/risks/next_actions`。
- 失败路径有清晰英文错误信息。
