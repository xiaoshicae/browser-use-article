"""任务执行 Agent — 封装完整的浏览器任务执行流程"""
from browser_use import Agent

from bu_task import browser
from bu_task.config import settings
from bu_task.llm import create_llm


async def run(task_content: str, model: str | None = None, max_steps: int = 0) -> None:
    """完整执行流程：关闭旧 Chrome → 启动新 Chrome → Agent.run → 关闭 Chrome"""
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
        browser.close_chrome()
