"""
bu-task — 基于 browser-use 的浏览器自动化任务框架

通过 Markdown 文件定义任务，自动启动 Chrome 并调用 LLM Agent 执行。

模块结构:
    config.py      - 项目配置（pydantic-settings，自动读取 .env）
    browser.py     - Chrome 启动与 CDP 连接
    task.py        - 任务文件解析（frontmatter + markdown）
    llm.py         - 共享 LLM 工具（提供商检测、LLM/客户端创建）
    generator.py   - 任务生成 Agent（一句话生成、润色优化）
    executor.py    - 任务执行 Agent（封装完整执行流程）
    cli.py         - CLI 入口（bu 命令）

快速使用:
    from bu_task.config import settings
    from bu_task import browser, task, generator, executor

配置优先级:
    环境变量 > .env 文件（从 cwd 向上递归查找）> 代码默认值

模型选择优先级:
    CLI -m 参数 > 任务文件 frontmatter model 字段 > settings.default_model
"""

__version__ = "0.1.0"
