# Week 3 MCP Server（脚手架）

本目录提供 Week 3 作业的标准化脚手架：先完成可运行的本地 STDIO 版本，再逐步接入真实外部 API。

## 1. 当前能力
- 提供两个工具入口（骨架）：
  - `get_current_weather`
  - `get_forecast`
- 已实现：参数校验、统一错误响应、STDIO 请求分发。
- 未实现：真实天气 API 接入（当前默认 mock 数据）。

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
    test_schemas.py
    test_tools.py
```

## 3. 运行方式（本地 STDIO）
在仓库根目录执行：

```powershell
python -m week3.server.main
```

输入一行 JSON 作为请求，例如：

```json
{"tool": "get_current_weather", "arguments": {"city": "Shanghai"}}
```

返回一行 JSON 结果。

## 4. 快速测试
在仓库根目录执行：

```powershell
pytest week3/tests -q
```

## 5. 下一步接入真实 API
- 在 `server/client.py` 中将 `use_mock_api=false` 时的请求逻辑替换为真实天气 API。
- 在 `server/config.py` 中配置 `WEATHER_API_KEY` 与 `WEATHER_BASE_URL`。
- 在 `server/tools.py` 中补充更细粒度的错误映射与输出字段。

## 6. Claude Desktop/Cursor 集成说明（待补充）
当前先保证本地脚手架可运行；真实 MCP SDK 接入与客户端配置将在下一阶段补齐。

