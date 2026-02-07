"""项目配置，所有字段均可通过同名环境变量或 .env 文件覆盖"""
import platform
import shutil
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_files() -> list[Path]:
    """从当前工作目录向上递归查找所有 .env 文件（近的优先级高）"""
    found = []
    current = Path.cwd()
    while True:
        env = current / ".env"
        if env.is_file():
            found.append(env)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return found


def _detect_chrome_path() -> str:
    """跨平台检测 Chrome 可执行文件路径"""
    system = platform.system()

    if system == "Darwin":
        candidates = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
    elif system == "Windows":
        candidates = [
            str(Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe"),
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]
    else:  # Linux
        candidates = [
            "google-chrome",
            "google-chrome-stable",
            "chromium",
            "chromium-browser",
        ]

    for c in candidates:
        p = Path(c)
        if p.is_absolute() and p.exists():
            return str(p)
        found = shutil.which(c)
        if found:
            return found

    if system == "Darwin":
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif system == "Windows":
        return "chrome.exe"
    return "google-chrome"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_find_env_files(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Chrome 浏览器
    chrome_path: str = _detect_chrome_path()
    chrome_user_data_dir: Path = Path.home() / ".chrome-debug-profile"
    cdp_port: int = 9222

    # LLM 提供商
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # 任务
    task_dir: Path = Path.cwd() / "task"
    default_model: str = "qwen-vl-max-latest"
    gen_model: str = "deepseek-chat"
    max_steps: int = 30


settings = Settings()
