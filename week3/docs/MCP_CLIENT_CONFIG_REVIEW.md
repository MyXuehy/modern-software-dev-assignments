# MCP 客户端配置审阅版（Codex / GitHub Copilot）

本文档是 `week3` 的独立审阅材料，目标是让你快速确认：
- 本地 STDIO 服务如何接入 MCP 客户端
- Copilot 与 Codex 的配置差异如何映射
- 如何用最小步骤验证联通

## 1. 适用范围
- 系统：Windows（PowerShell）
- 服务入口：`python -m week3.server.mcp_stdio`
- 协议现状：提供最小 MCP JSON-RPC 流程（initialize/tools/list/tools/call/ping）

## 2. 前置检查
在项目根目录 `D:\code\Python\CS146S` 下，先确认服务能单独启动：

```powershell
Set-Location "D:\code\Python\CS146S"
$env:USE_MOCK_API="false"
python -m week3.server.main
```

启动后手动输入一行请求：

```json
{"tool":"get_current_weather","arguments":{"city":"Shanghai"}}
```

如果返回 `{"ok": true, ...}` 结构，说明服务端可用。

## 3. GitHub Copilot 配置（JSON 风格）
说明：不同 IDE 版本的配置文件路径可能不同，以下给出最小字段模板。

```json
{
  "mcpServers": {
    "week3-weather": {
      "command": "python",
      "args": ["-m", "week3.server.mcp_stdio"],
      "cwd": "D:/code/Python/CS146S",
      "env": {
        "USE_MOCK_API": "false",
        "REQUEST_TIMEOUT_SECONDS": "8",
        "MAX_RETRIES": "2",
        "RETRY_BACKOFF_SECONDS": "0.4"
      }
    }
  }
}
```

字段意图：
- `command` + `args`：定义 STDIO 子进程入口
- `cwd`：保证 `week3` 包可导入
- `env`：固定重试/超时行为，便于复现实验结果

## 4. Codex 配置（TOML 风格）
说明：不同客户端可能写成 `mcp_servers` 或等价命名，核心仍是 `command/args/env`。

```toml
[mcp_servers.week3_weather]
command = "python"
args = ["-m", "week3.server.mcp_stdio"]
cwd = "D:\\code\\Python\\CS146S"
env = { USE_MOCK_API = "false", REQUEST_TIMEOUT_SECONDS = "8", MAX_RETRIES = "2", RETRY_BACKOFF_SECONDS = "0.4" }
```

## 5. 联通验证清单（建议逐条打勾）
- [ ] 客户端能拉起 `week3-weather` 进程且不中断
- [ ] 工具列表可见 `get_current_weather` 与 `get_forecast`
- [ ] 能成功调用一次当前天气
- [ ] 能成功调用一次 3 天天气预报
- [ ] 非法参数能返回结构化错误（如 `days=99`）

可用于客户端触发的示例请求：

```json
{"tool":"get_current_weather","arguments":{"city":"Shanghai"}}
```

```json
{"tool":"get_forecast","arguments":{"city":"Shanghai","days":3}}
```

```json
{"tool":"get_forecast","arguments":{"city":"Shanghai","days":99}}
```

## 6. 常见问题与定位
1. 客户端看不到工具
   - 检查 `cwd` 是否为项目根目录
   - 检查 `python` 是否指向当前虚拟环境
2. 调用超时
   - 检查网络连通性
   - 增大 `REQUEST_TIMEOUT_SECONDS`（例如 `12`）
3. 返回 `rate_limited`
   - 说明上游限流已触发，等待后重试
   - 可临时调大 `RETRY_BACKOFF_SECONDS`

## 7. 审阅结论建议模板
你审阅时可按下面模板记录：

```text
- 配置可读性：通过 / 不通过
- 最小可运行性：通过 / 不通过
- 兼容性提示充分性：通过 / 不通过
- 待修改项：...
```

---
若后续需要对接“标准 MCP 握手”客户端（要求 initialize/resources/prompts），建议新增标准 SDK 入口文件，与当前课程版入口并行维护。
