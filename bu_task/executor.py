"""任务执行 Agent — 封装完整的浏览器任务执行流程"""
import atexit
import signal
import sys

from browser_use import Agent

from bu_task import browser
from bu_task.config import settings
from bu_task.llm import create_llm

# 全局标记，防止重复关闭
_cleanup_done = False


def _cleanup():
    """清理函数：关闭浏览器"""
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True
    print("\n🧹 正在清理...")
    browser.close_chrome()


def _signal_handler(signum, frame):
    """信号处理：捕获 SIGTERM/SIGINT 时关闭浏览器"""
    _cleanup()
    sys.exit(128 + signum)


# 注册信号处理和退出钩子
signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)
atexit.register(_cleanup)


async def run(task_content: str, model: str | None = None, max_steps: int = 0) -> None:
    """完整执行流程：关闭旧 Chrome → 启动新 Chrome → Agent.run → 关闭 Chrome"""
    global _cleanup_done
    _cleanup_done = False  # 重置标记

    model = model or settings.default_model
    steps = max_steps or settings.max_steps

    # 先关闭旧实例，确保干净环境
    browser.close_chrome()

    if not browser.ensure_chrome():
        return

    llm, use_vision = create_llm(model)
    session = browser.create_session()

    try:
        agent = Agent(task=task_content, llm=llm, browser=session, use_vision=use_vision)
        await agent.run(max_steps=steps)
        print("✅ 任务完成")
    finally:
        _cleanup()
