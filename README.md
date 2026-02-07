# bu-task

用 Markdown 定义浏览器自动化任务，LLM Agent 操控 Chrome 执行。

## 使用

```bash
./bu.sh list                          # 列出所有任务
./bu.sh run 小红书                     # 执行已有任务（模糊匹配）
./bu.sh do "在小红书发一篇AI趋势长文"    # 生成并执行
./bu.sh gen "在豆瓣搜索科幻电影"         # 只生成不执行
./bu.sh polish 小红书                  # 润色已有任务
```

任务文件在 `task/*.md`，执行效果不好时直接编辑对应文件优化步骤即可。
