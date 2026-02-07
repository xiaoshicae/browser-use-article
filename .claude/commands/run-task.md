---
description: 运行 Browser-Use Agent 执行指定任务
user-invocable: true
---

# 运行 Browser-Use 任务

执行 `task/` 目录下定义的自动化任务。

## 参数

$ARGUMENTS - 任务名称（可选，支持模糊匹配，不含 .md 后缀）

## 执行

```bash
if [ -n "$ARGUMENTS" ]; then
    cd /Users/zs/Workspace/myproject/browser-use && .venv/bin/bu run "$ARGUMENTS"
else
    cd /Users/zs/Workspace/myproject/browser-use && .venv/bin/bu list
fi
```

## 用法示例

- `/run-task` - 列出所有可用任务
- `/run-task EigenAI模型文档整理` - 执行指定任务
- `/run-task eigen` - 模糊匹配任务名

## CLI 用法

```
bu list                          # 列出所有任务
bu run <名称> [-m 模型]           # 运行任务
bu gen "描述" [-m 模型]           # AI 生成任务
bu gen "描述" --preview           # 只预览，不保存
bu do "描述" [-m 模型]            # 生成 + 自动执行
bu polish <名称> [-m 模型]        # 润色已有任务
bu init                          # 初始化任务目录
```

## 模型选择优先级

CLI `-m` > 任务文件 frontmatter `model` > config `DEFAULT_MODEL`(qwen-vl-max-latest)
