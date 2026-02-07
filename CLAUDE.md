# bu-task 项目

基于 browser-use 库的浏览器自动化框架。通过 Markdown 文件定义任务，自动启动 Chrome 并调用 LLM Agent 执行。

PyPI 包名：`bu-task`，模块名：`bu_task`，CLI 命令：`bu`

## 项目结构

```
browser-use/
├── pyproject.toml          # 构建配置（hatchling）
├── README.md               # 项目说明
├── LICENSE                 # MIT
├── .env                    # API 密钥配置（不打包）
├── .venv/                  # Python 虚拟环境（不打包）
├── bu_task/                # 核心模块（PyPI 包）
│   ├── __init__.py         # 版本号与模块说明
│   ├── config.py           # pydantic-settings 配置（自动读取 .env）
│   ├── browser.py          # Chrome 启动与 CDP 连接
│   ├── task.py             # 任务文件解析（frontmatter + markdown）
│   ├── llm.py             # 共享 LLM 工具（提供商检测、LLM/客户端创建）
│   ├── generator.py       # 任务生成 Agent（一句话生成、润色优化）
│   ├── executor.py        # 任务执行 Agent（封装完整执行流程）
│   ├── cli.py              # CLI 入口（bu 命令）
│   └── templates/          # 内置示例任务（随包分发）
│       └── example.md
├── task/                   # 用户任务目录（不打包）
│   └── *.md
└── .claude/
    └── commands/
        └── run-task.md     # /run-task 命令
```

## CLI 用法

```bash
# 列出所有可用任务
bu list

# 运行指定任务（模糊匹配）
bu run eigen

# 覆盖任务中的模型配置
bu run 发布小红书 -m gpt-4o

# AI 生成任务（自动命名）
bu gen "在小红书发一篇关于AI趋势的长文"

# 只预览生成结果，不保存
bu gen "在豆瓣搜索科幻电影" --preview

# 生成任务并自动执行
bu do "在百度搜索今日新闻"

# 润色已有任务
bu polish 豆瓣

# 初始化任务目录和示例文件
bu init
```

## 开发运行

```bash
# 可编辑安装
.venv/bin/pip install -e .

# 然后直接使用 bu 命令
.venv/bin/bu list
```

## Claude Command

```bash
/run-task              # 列出所有任务
/run-task 任务名        # 执行指定任务
```

## 配置说明

所有配置项通过 `bu_task/config.py` 的 `Settings` 类管理（pydantic-settings），支持环境变量和 .env 文件覆盖。

### 可配置项

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| CHROME_PATH | (跨平台自动检测) | Chrome 可执行文件路径 |
| CHROME_USER_DATA_DIR | ~/.chrome-debug-profile | Chrome 用户数据目录 |
| CDP_PORT | 9222 | CDP 调试端口 |
| OPENAI_API_KEY | - | OpenAI API 密钥 |
| DEEPSEEK_API_KEY | - | DeepSeek API 密钥 |
| QWEN_API_KEY | - | 通义千问 API 密钥 |
| QWEN_BASE_URL | https://dashscope.aliyuncs.com/compatible-mode/v1 | 千问 API 地址 |
| TASK_DIR | ./task（当前工作目录） | 任务文件目录 |
| DEFAULT_MODEL | qwen-vl-max-latest | 默认模型 |
| GEN_MODEL | deepseek-chat | 任务生成用模型（不需要视觉，便宜快速） |
| MAX_STEPS | 30 | Agent 最大执行步数（防死循环） |

### .env 查找逻辑

从当前工作目录向上递归查找所有 `.env` 文件，近处优先。

### 模型选择优先级

CLI `-m` 参数 > 任务文件 frontmatter `model` 字段 > `DEFAULT_MODEL`

### 模型名自动识别提供商

| 模型名包含 | 提供商 | LLM 类 | 视觉 |
|-----------|--------|--------|------|
| qwen | 通义千问 | ChatOpenAI | 支持 |
| deepseek | DeepSeek | ChatDeepSeek | 不支持 |
| 其它 | OpenAI | ChatOpenAI | 支持 |

### 代理注意事项

程序自动设置 `NO_PROXY=localhost,127.0.0.1`，避免 CDP 连接超时。

## 任务文件格式

在 `task/` 目录下创建 `.md` 文件：

```markdown
---
description: 任务简短描述（显示在列表中）
model: qwen-vl-max-latest
url: https://example.com
output_format: json
---

# 任务详细描述

具体的任务指令，Agent 会读取这部分内容执行。
```

### frontmatter 字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| description | string | "" | 任务描述 |
| model | string | (读取配置) | 使用的模型 |
| url | string | "" | 目标网站（参考） |
| output_format | string | json | 输出格式 |
| max_steps | int | (读取配置,默认30) | 最大执行步数（防死循环） |

## 模块 API

### bu_task/config.py
- `settings` — 全局配置实例（`Settings` 类，pydantic-settings）

### bu_task/browser.py
- `ensure_chrome()` — 确保 Chrome 调试实例已启动
- `create_session()` — 创建 BrowserSession（CDP 连接）

### bu_task/task.py
- `load(name)` — 按名称模糊匹配加载任务，返回 dict（name/content/model/...）
- `list_all()` — 列出所有任务，返回 [(名称, 描述), ...]

### bu_task/llm.py
- `detect_provider(model)` — 通过模型名推断提供商
- `create_llm(model)` — 根据模型名创建 LangChain LLM，返回 (llm, use_vision)
- `create_client(model)` — 创建 OpenAI 兼容客户端（用于文本生成）

### bu_task/generator.py
- `generate(description, model)` — 一句话 → 完整任务 Markdown
- `polish(task_content, model)` — 润色/优化已有任务内容
- `preview(content)` — 格式化预览任务内容到 stdout
- `save(name, content)` — 保存到 task/ 目录，返回文件路径
- `suggest_name(content)` — 从 frontmatter description 提取文件名

### bu_task/executor.py
- `run(task_content, model, max_steps)` — 完整执行流程（ensure_chrome → create_llm → create_session → Agent.run）

## 打包发布

```bash
# 构建
python -m build

# 发布到 PyPI
python -m twine upload dist/*
```

## 参考

- 官方文档: https://docs.browser-use.com
