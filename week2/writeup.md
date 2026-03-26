# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
```
1) 阅读 assignment，为 TODO1 列一个详细的修改计划。
2) 你可以借用这个文件中的调用，完成 TODO1 的功能。
3) 修改接口，使得原来的接口能够调用到新的函数。
``` 

Generated Code Snippets:
```
week2/app/services/extract.py
- L20-L25: 增加 LLM 默认模型和 system prompt
- L67-L92: 新增 extract_action_items_llm(text)（Ollama chat + structured output + fallback）
- L117-L129: 新增 _parse_llm_items(raw) 解析 JSON 输出
- L131-L141: 新增 _dedupe_items(items) 去重

week2/app/routers/action_items.py
- L17: 原接口改为引入 extract_action_items_llm
- L30: /action-items/extract 改为调用 extract_action_items_llm(text)
```

### Exercise 2: Add Unit Tests
Prompt: 
```
继续完成第二个 TODO，为它编写单元测试。
``` 

Generated Code Snippets:
```
week2/tests/test_extract.py
- L22-L48: test_extract_action_items_llm_bullets（bullet/checkbox 场景，断言 format/options）
- L50-L69: test_extract_action_items_llm_keyword_lines（TODO/ACTION/NEXT 场景）
- L71-L79: test_extract_action_items_llm_empty_input_does_not_call_chat（空输入）
- L81-L92: test_extract_action_items_llm_falls_back_on_chat_error（Ollama 异常回退）

验证结果：
- 运行 week2 tests 后全部通过（本地记录：9 passed）
```

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
继续实现 TODO3，注意里面的 focusing 的内容。
``` 

Generated/Modified Code Snippets:
```
week2/app/schemas.py
- L8: 新增 NonEmptyString 约束（strip + min_length）
- L15-L54: 新增 Note/Extract/ActionItem/MarkDone 等请求响应 schema

week2/app/routers/notes.py
- L13-L27: 路由改为 typed request/response + response_model
- L18/L26: 使用 NotFoundError 统一 404

week2/app/routers/action_items.py
- L23-L35: /extract 改为 typed contract（ExtractRequest -> ExtractResponse）
- L38-L41: /action-items 列表返回 ActionItemResponse
- L44-L49: /done 返回 MarkDoneResponse；不存在时抛 404

week2/app/db.py
- L12-L29: 抽离建表 SQL 常量，清理数据库层结构
- L61-L76: 新增 row mapper（_to_note/_to_action_item）
- L79-L127: list/get 返回结构化 dict
- L129-L137: mark_action_item_done 改为返回 bool（支持上层 error handling）

week2/app/config.py
- L9-L22: 新增 Settings/get_settings，集中 app 配置

week2/app/errors.py
- L13-L37: 新增 NotFoundError/BadRequestError 与统一异常处理注册

week2/app/main.py
- L15-L19: 使用 lifespan 启动周期初始化 DB
- L21-L37: 新增 create_app() 工厂，注册路由、静态资源和异常处理器

week2/tests/test_api.py
- L18-L22: 非空内容校验（422）
- L25-L30: note not found（404）
- L33-L46: extract 返回 typed payload
- L49-L54: action item not found（404）
```


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
``` 

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 