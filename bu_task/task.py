"""任务文件读取与解析"""
from pathlib import Path

from bu_task.config import settings


def load(name: str) -> dict:
    """按名称模糊匹配加载任务，返回解析后的任务字典"""
    matches = [f for f in settings.task_dir.glob("*.md") if name.lower() in f.stem.lower()]
    if not matches:
        raise FileNotFoundError(f"未找到匹配任务: {name}")
    if len(matches) > 1:
        raise ValueError(f"匹配到多个任务: {[f.stem for f in matches]}")
    return _parse(matches[0])


def list_all() -> list[tuple[str, str]]:
    """列出所有任务，返回 [(名称, description), ...]"""
    result = []
    for f in sorted(settings.task_dir.glob("*.md")):
        meta, _ = _parse_frontmatter(f.read_text(encoding="utf-8"))
        result.append((f.stem, meta.get("description", "")))
    return result


def _parse(path: Path) -> dict:
    """解析任务文件，返回 {name, content, model, description, ...}"""
    text = path.read_text(encoding="utf-8")
    meta, content = _parse_frontmatter(text)
    return {
        "name": path.stem,
        "content": content,
        "model": meta.get("model", ""),
        "description": meta.get("description", ""),
        "url": meta.get("url", ""),
        "output_format": meta.get("output_format", "json"),
        "max_steps": int(meta.get("max_steps", 0)),
    }


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """拆分 frontmatter 和正文，返回 (meta_dict, content)"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip()
    return meta, parts[2].strip()
