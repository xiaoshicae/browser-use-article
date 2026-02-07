"""CLI 入口 — bu 命令"""
import argparse
import asyncio
import shutil
from pathlib import Path

from bu_task import task, generator, executor
from bu_task.config import settings


def main():
    parser = argparse.ArgumentParser(
        prog="bu",
        description="bu-task: 基于 browser-use 的浏览器自动化任务运行器",
    )
    sub = parser.add_subparsers(dest="command")

    # bu list
    sub.add_parser("list", help="列出所有可用任务")

    # bu run
    p_run = sub.add_parser("run", help="运行指定任务")
    p_run.add_argument("task_name", help="任务名称（支持模糊匹配）")
    p_run.add_argument("-m", "--model", help="覆盖模型名称")

    # bu gen
    p_gen = sub.add_parser("gen", help="AI 生成任务文件")
    p_gen.add_argument("description", help="一句话描述任务")
    p_gen.add_argument("-m", "--model", help="生成用模型名称")
    p_gen.add_argument("--preview", action="store_true", help="只预览，不保存")

    # bu do
    p_do = sub.add_parser("do", help="生成任务并自动执行")
    p_do.add_argument("description", help="一句话描述任务")
    p_do.add_argument("-m", "--model", help="模型名称")

    # bu polish
    p_polish = sub.add_parser("polish", help="润色已有任务")
    p_polish.add_argument("task_name", help="任务名称（支持模糊匹配）")
    p_polish.add_argument("-m", "--model", help="润色用模型名称")

    # bu init
    sub.add_parser("init", help="初始化 task/ 目录和示例文件")

    args = parser.parse_args()

    if args.command == "list":
        _list_tasks()
    elif args.command == "run":
        _run_task(args.task_name, args.model)
    elif args.command == "gen":
        _gen_task(args.description, args.model, args.preview)
    elif args.command == "do":
        _do_task(args.description, args.model)
    elif args.command == "polish":
        _polish_task(args.task_name, args.model)
    elif args.command == "init":
        _init()
    else:
        parser.print_help()


def _list_tasks():
    tasks = task.list_all()
    if not tasks:
        print("没有找到任务文件。运行 `bu init` 创建示例任务。")
        return
    for name, desc in tasks:
        print(f"  {name:30s}  {desc}")


def _run_task(task_name: str, model: str | None = None):
    t = task.load(task_name)
    model = model or t["model"] or settings.default_model

    print(f"任务: {t['name']}")
    print(f"模型: {model}")
    print()

    asyncio.run(executor.run(t["content"], model, t.get("max_steps", 0)))


def _gen_task(description: str, model: str | None = None, preview_only: bool = False):
    """AI 生成任务文件"""
    if not preview_only:
        existing = generator.find_similar(description, model)
        if existing:
            print(f"发现类似任务: {existing['name']}")
            print("正在更新优化...")
            new_content = generator.polish(existing["content"], model)
            path = generator.save(existing["name"], new_content)
            print(f"已更新: {path}")
            return

    print("正在生成任务...")
    content = generator.generate(description, model)

    if preview_only:
        generator.preview(content)
        return

    name = generator.suggest_name(content)
    path = generator.save(name, content)
    print(f"已保存: {path}")


def _do_task(description: str, model: str | None = None):
    """生成任务并自动执行"""
    existing = generator.find_similar(description, model)
    if existing:
        print(f"发现类似任务: {existing['name']}")
        print("正在更新优化...")
        content = generator.polish(existing["content"], model)
        path = generator.save(existing["name"], content)
        print(f"已更新: {path}")
    else:
        print("正在生成任务...")
        content = generator.generate(description, model)
        name = generator.suggest_name(content)
        path = generator.save(name, content)
        print(f"已保存: {path}")
    print()

    # 从生成内容中提取模型配置，否则用默认执行模型
    from bu_task.task import _parse_frontmatter
    meta, body = _parse_frontmatter(content)
    exec_model = model or meta.get("model") or settings.default_model

    print(f"模型: {exec_model}")
    print("开始执行...")
    print()

    asyncio.run(executor.run(content, exec_model))


def _polish_task(task_name: str, model: str | None = None):
    """润色已有任务"""
    t = task.load(task_name)
    print(f"正在润色任务: {t['name']}...")
    print()

    new_content = generator.polish(t["content"], model)

    path = generator.save(t["name"], new_content)
    print(f"已保存: {path}")


def _init():
    """初始化 task/ 目录，复制示例任务文件"""
    task_dir = settings.task_dir
    task_dir.mkdir(parents=True, exist_ok=True)

    # 复制内置示例文件
    templates_dir = Path(__file__).parent / "templates"
    if templates_dir.is_dir():
        for tpl in templates_dir.glob("*.md"):
            dest = task_dir / tpl.name
            if not dest.exists():
                shutil.copy2(tpl, dest)
                print(f"  已创建: {dest}")
            else:
                print(f"  已存在: {dest}")

    print(f"任务目录已就绪: {task_dir}")


if __name__ == "__main__":
    main()
