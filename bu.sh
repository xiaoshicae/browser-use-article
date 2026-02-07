#!/bin/bash
# bu-task 快速启动脚本
# 用法:
#   ./bu.sh list                          列出所有任务
#   ./bu.sh run 小红书                     执行已有任务（模糊匹配）
#   ./bu.sh do "在小红书发一篇AI趋势长文"    生成并执行
#   ./bu.sh gen "在豆瓣搜索科幻电影"         只生成不执行
#   ./bu.sh polish 小红书                  润色已有任务

cd "$(dirname "$0")"

if [ ! -f .venv/bin/bu ]; then
    echo "首次运行，正在初始化环境..."
    python3 -m venv .venv
    .venv/bin/pip install -e .
fi

exec .venv/bin/bu "$@"
