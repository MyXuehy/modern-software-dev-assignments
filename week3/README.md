# Week 3 MCP Server（Open-Meteo）

本目录已接入 Open-Meteo 真实天气 API（默认仍可使用 mock 模式）。

## 1. 当前能力
- 提供两个工具入口：
  - `get_current_weather`
  - `get_forecast`
- 已实现：参数校验、统一错误响应、STDIO 请求分发、真实 API 调用、重试与超时处理。

## 2. 目录结构
```text
week3/
  README.md
  PROJECT_PLAN.md
  server/
    __init__.py
    main.py
    config.py
    errors.py
    schemas.py
    client.py
    tools.py
  tests/
    __init__.py
    test_client.py
    test_schemas.py
    test_tools.py
```

## 3. 环境变量
Open-Meteo 免费接口默认不需要 API Key。

- `USE_MOCK_API`：`true/false`，默认 `true`
- `WEATHER_BASE_URL`：默认 `https://api.open-meteo.com/v1`
- `GEOCODING_BASE_URL`：默认 `https://geocoding-api.open-meteo.com/v1`
- `REQUEST_TIMEOUT_SECONDS`：默认 `8`
- `MAX_RETRIES`：默认 `2`
- `RETRY_BACKOFF_SECONDS`：默认 `0.4`

## 4. 运行方式（本地 STDIO）
在仓库根目录执行：

```powershell
python -m week3.server.main
```

输入一行 JSON 作为请求，例如：

```json
{"tool": "get_current_weather", "arguments": {"city": "Shanghai"}}
```

返回一行 JSON 结果。

示例（查询 3 天预报）：

```json
{"tool": "get_forecast", "arguments": {"city": "Shanghai", "days": 3}}
```

若要启用真实 API：

```powershell
$env:USE_MOCK_API="false"
python -m week3.server.main
```

## 5. 快速测试
在仓库根目录执行：

```powershell
pytest week3/tests -q
```

## 6. 调用流程
```mermaid
flowchart LR
    A[STDIN 输入 tool 调用 JSON] --> B[main.py 解析请求]
    B --> C[tools.py 选择工具并校验参数]
    C --> D[client.py 先做地理编码]
    D --> E[client.py 查询 forecast/current]
    E --> F[返回结构化天气结果]
    C --> G[异常映射为结构化错误]
    G --> H[STDOUT 返回 JSON 错误]
    F --> H2[STDOUT 返回 JSON 成功]
```

## 7. Claude Desktop/Cursor 集成说明（待补充）
当前先保证本地脚手架可运行；真实 MCP SDK 接入与客户端配置将在下一阶段补齐。

