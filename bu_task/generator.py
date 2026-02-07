"""任务生成 Agent — 一句话生成任务、润色已有任务、去重检查"""
import re
from pathlib import Path

from bu_task.config import settings
from bu_task.llm import create_client
from bu_task.task import _parse_frontmatter
from bu_task import task

GENERATE_PROMPT = """\
你是一个浏览器自动化任务生成器。根据用户的一句话描述，生成完整的任务文件（Markdown 格式）。

输出格式要求：
1. 以 YAML frontmatter 开头（---包裹），必须包含 description 字段（简短描述任务）
2. frontmatter 可选字段：model、url、output_format、max_steps
3. 正文部分写清晰的分步骤指令，Agent 会按照这些指令操作浏览器

示例输出：
---
description: 在豆瓣搜索评分最高的科幻电影
url: https://www.douban.com
model: qwen-vl-max-latest
---

# 在豆瓣搜索评分最高的科幻电影

1. 打开豆瓣电影页面 https://movie.douban.com
2. 在搜索框中输入"科幻"
3. 点击搜索按钮
4. 按评分从高到低排序
5. 记录前10部电影的名称和评分

## 小红书任务特殊规则

如果任务涉及小红书发布，必须遵循以下模板：
- frontmatter 中设置 model: qwen-vl-max-latest（小红书页面复杂，需要强视觉模型）
- url 设为 `https://www.xiaohongshu.com`
- 步骤 1：访问 `https://creator.xiaohongshu.com/publish/publish`，等待 3 秒让页面完全加载
- 步骤 2：如果需要登录，等待用户手动登录后继续
- 步骤 3：选择发布类型。"写长文"是页面顶部的 tab 标签，点击后会出现"新的创作"按钮，必须再点击"新的创作"才能进入编辑器
- 步骤 4：智能标题填入 #${title} (${title}是文章相关的话题，比如#人工智能 #AI 等，填入2-3个相关的话题就行) 
- 步骤 5：完成后点击页面下方的 "发布" 红色按钮，页面跳转说明发布成功
- 内容填写：先填标题，再填正文，用代码块包裹具体文案内容
- 添加话题标签：每个话题标签不超过20个字，逐个输入并从下拉建议中选择
- 注意事项必须包含：遇到登录页面暂停等待用户操作；页面布局与预期不同时灵活适应；不要自动点击发布按钮

注意：
- 只输出 Markdown 内容，不要输出其他解释文字
- 小红书 "文字" 类型文章有500字限制
- 文案内容严格控制空行：段落之间最多1个空行，禁止连续多个空行，段落内部不要空行，保持紧凑排版
- description 字段要简洁，不超过20个字
- 步骤要具体可操作，适合浏览器 Agent 执行
"""

POLISH_PROMPT = """\
你是浏览器自动化任务优化器。对用户已有的任务文件进行润色优化：

1. 保持原始意图不变
2. 补充缺失的 frontmatter 字段（description、url 等）
3. 细化模糊步骤，使其更具可操作性
4. 添加异常处理提示（如登录、弹窗等）
5. 优化步骤顺序和表述

输出要求：
- 输出完整的优化后 Markdown（包含 frontmatter）
- 不要输出解释文字，只输出任务内容
- 保持 frontmatter 的 --- 包裹格式
"""


def generate(description: str, model: str | None = None) -> str:
    """ 一句话 → 完整任务 Markdown """
    model = model or settings.gen_model
    client = create_client(model)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": GENERATE_PROMPT},
            {"role": "user", "content": description},
        ],
    )
    draft = resp.choices[0].message.content.strip()
    return polish(draft, model)


def polish(task_content: str, model: str | None = None) -> str:
    """ 润色/优化 已有任务内容 """
    model = model or settings.gen_model
    client = create_client(model)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": POLISH_PROMPT},
            {"role": "user", "content": task_content},
        ],
    )
    return resp.choices[0].message.content.strip()


SIMILAR_CHECK_PROMPT = """\
你是任务去重检查器。比较用户想要创建的新任务描述与已有任务列表，判断是否存在语义相似的任务。

已有任务列表：
{task_list}

判断规则：
- 如果某个任务与新描述的目标、平台、内容主题基本一致，视为"相似"
- 仅平台相同但内容完全不同的，不算相似

只输出一行结果：
- 如果没有相似任务：none
- 如果有相似任务：任务名称（精确匹配列表中的名称）
"""


def find_similar(description: str, model: str | None = None) -> dict | None:
    """检查已有任务中是否存在与 description 相似的任务，返回匹配的任务 dict 或 None"""
    tasks = task.list_all()
    if not tasks:
        return None

    task_list = "\n".join(f"- {name}: {desc}" for name, desc in tasks)
    prompt = SIMILAR_CHECK_PROMPT.format(task_list=task_list)

    model = model or settings.gen_model
    client = create_client(model)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": description},
        ],
    )
    result = resp.choices[0].message.content.strip()

    if result.lower() == "none":
        return None

    # 尝试用返回的名称加载任务
    try:
        return task.load(result)
    except (FileNotFoundError, ValueError):
        return None


def preview(content: str) -> None:
    """格式化预览任务内容到 stdout"""
    meta, body = _parse_frontmatter(content)
    # frontmatter 部分
    if meta:
        print("---")
        for k, v in meta.items():
            print(f"  {k}: {v}")
        print("---")
    # 正文部分
    if body:
        print()
        print(body)


def save(name: str, content: str) -> Path:
    """保存任务内容到 task/ 目录，返回文件路径"""
    path = settings.task_dir / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def suggest_name(content: str) -> str:
    """从生成内容的 frontmatter description 提取文件名"""
    meta, _ = _parse_frontmatter(content)
    desc = meta.get("description", "").strip()
    if not desc:
        return "未命名任务"
    # 去除文件名不安全字符
    name = re.sub(r'[\\/:*?"<>|]', "", desc)
    return name[:50] or "未命名任务"
