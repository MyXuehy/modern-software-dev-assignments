# /p3-complete-flow

目标：围绕 P3（`PUT /action-items/{id}/complete`）执行“测试优先 -> 最小实现 -> 回归验证 -> 结果摘要”。

参考：
- Claude Code best practices: https://www.anthropic.com/engineering/claude-code-best-practices
- SubAgents overview: https://docs.anthropic.com/en/docs/claude-code/sub-agents

## Inputs
- `scope`: `backend|frontend|full`（默认 `full`）
- `test_target`: 默认 `backend/tests/test_action_items.py`
- `strict404`: `true|false`（默认 `true`）

## Defaults
- 如果未提供参数，按 `scope=full test_target=backend/tests/test_action_items.py strict404=true` 执行。

## Invalid Input Handling
- `scope` 非法时回退到 `full` 并在输出 `risks` 标注。
- `test_target` 不存在时立即停止，返回 `status=failed`。

## Stop Conditions
- 任何测试失败即停止后续步骤。
- 出现安全 denylist 命令请求时直接拒绝。

## Safety
- 允许：`pytest`、`ruff check`、`black --check`、只读文件查看。
- 禁止：`rm -rf`、`git reset --hard`、`git clean -fd`、非必要数据库写入。

## Workflow
1. 先运行 `test_target`，确认基线。
2. 若 P3 缺少边界测试：补充 `404` 与幂等用例。
3. 仅在必要时修改实现，保证错误信息英文。
4. 运行相关测试，最后可选全量测试。
5. 输出结构化结果。

## Output Schema
- `status`: `passed|failed|blocked`
- `summary`: 一句话结论
- `artifacts`: 修改文件列表
- `risks`: 风险/未决项
- `next_actions`: 下一步建议

## Success Example
- 输入：`scope=backend strict404=true`
- 输出：
  - `status=passed`
  - `artifacts=[backend/tests/test_action_items.py]`
  - `summary=P3 edge cases covered with English 404 detail`

## Failure Example
- 输入：`test_target=backend/tests/not_exists.py`
- 输出：
  - `status=failed`
  - `summary=Test target not found`

## Idempotency Example
- 相同输入重复执行两次，第二次应输出 `artifacts=[]` 或仅包含非功能性变更。
