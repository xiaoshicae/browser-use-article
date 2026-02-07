"""共享 LLM 工具 — 提供商检测、LangChain LLM 创建、OpenAI 兼容客户端"""
from openai import OpenAI
from browser_use.llm import ChatOpenAI, ChatDeepSeek

from bu_task.config import settings

# 提供商配置
PROVIDERS = {
    "qwen": {
        "api_key": settings.qwen_api_key,
        "base_url": settings.qwen_base_url,
        "cls": ChatOpenAI,
        "vision": True,
    },
    "deepseek": {
        "api_key": settings.deepseek_api_key,
        "base_url": "https://api.deepseek.com",
        "cls": ChatDeepSeek,
        "vision": False,
    },
    "openai": {
        "api_key": settings.openai_api_key,
        "cls": ChatOpenAI,
        "vision": True,
    },
}


def detect_provider(model: str) -> str:
    """通过模型名推断提供商"""
    m = model.lower()
    if "qwen" in m:
        return "qwen"
    if "deepseek" in m:
        return "deepseek"
    return "openai"


def create_llm(model: str):
    """根据模型名创建 LangChain LLM 实例，返回 (llm, use_vision)"""
    provider = detect_provider(model)
    conf = PROVIDERS[provider]

    kwargs = {"model": model, "api_key": conf["api_key"]}
    if "base_url" in conf:
        kwargs["base_url"] = conf["base_url"]

    return conf["cls"](**kwargs), conf["vision"]


def create_client(model: str) -> OpenAI:
    """根据模型名创建 OpenAI 兼容客户端（用于文本生成）"""
    provider = detect_provider(model)
    conf = PROVIDERS[provider]

    kwargs = {"api_key": conf["api_key"]}
    if "base_url" in conf:
        kwargs["base_url"] = conf["base_url"]

    return OpenAI(**kwargs)
