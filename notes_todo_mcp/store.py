"""
本地 JSON 文件存储层
数据保存在项目根目录的 note/ 目录下
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _find_project_root() -> Path:
    """向上查找 pyproject.toml 所在目录作为项目根，比 parent.parent 更健壮"""
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    # 兜底：回退到原来的相对路径方式
    return Path(__file__).resolve().parent.parent


DATA_DIR = _find_project_root() / "note"
NOTES_FILE = DATA_DIR / "notes.json"
TODOS_FILE = DATA_DIR / "todos.json"


def _ensure_data_dir() -> None:
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(filepath: Path) -> list[dict]:
    """从 JSON 文件加载数据"""
    logger.debug("[Store] _load_json | path=%s, exists=%s", filepath.resolve(), filepath.exists())
    if not filepath.exists():
        return []
    text = filepath.read_text(encoding="utf-8")
    if not text.strip():
        return []
    return json.loads(text)


def _save_json(filepath: Path, data: list[dict]) -> None:
    """将数据写入 JSON 文件"""
    _ensure_data_dir()
    logger.debug("[Store] _save_json | path=%s, count=%d", filepath.resolve(), len(data))
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _now_iso() -> str:
    """返回当前 UTC 时间的 ISO 格式字符串"""
    return datetime.now(timezone.utc).isoformat()


# ──────────────────────────────────────
#  笔记 (Notes) CRUD
# ──────────────────────────────────────

def create_note(title: str, content: str, tags: Optional[list[str]] = None) -> dict:
    """创建一条新笔记"""
    logger.debug("[Store] create_note | title=%s, tags=%s", title, tags)
    notes = _load_json(NOTES_FILE)
    note = {
        "id": uuid.uuid4().hex[:8],
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    notes.append(note)
    _save_json(NOTES_FILE, notes)
    return note


def list_notes(tag: Optional[str] = None) -> list[dict]:
    """列出所有笔记，可按标签筛选"""
    logger.debug("[Store] list_notes | tag=%s", tag)
    notes = _load_json(NOTES_FILE)
    if tag:
        notes = [n for n in notes if tag in n.get("tags", [])]
    return notes


def get_note(note_id: str) -> Optional[dict]:
    """根据 ID 获取笔记详情"""
    logger.debug("[Store] get_note | note_id=%s", note_id)
    notes = _load_json(NOTES_FILE)
    for n in notes:
        if n["id"] == note_id:
            return n
    return None


def update_note(note_id: str, title: Optional[str] = None,
                content: Optional[str] = None,
                tags: Optional[list[str]] = None) -> Optional[dict]:
    """更新笔记内容"""
    logger.debug("[Store] update_note | note_id=%s", note_id)
    notes = _load_json(NOTES_FILE)
    for n in notes:
        if n["id"] == note_id:
            if title is not None:
                n["title"] = title
            if content is not None:
                n["content"] = content
            if tags is not None:
                n["tags"] = tags
            n["updated_at"] = _now_iso()
            _save_json(NOTES_FILE, notes)
            return n
    return None


def delete_note(note_id: str) -> bool:
    """删除一条笔记"""
    logger.debug("[Store] delete_note | note_id=%s", note_id)
    notes = _load_json(NOTES_FILE)
    original_len = len(notes)
    notes = [n for n in notes if n["id"] != note_id]
    if len(notes) < original_len:
        _save_json(NOTES_FILE, notes)
        return True
    return False


def search_notes(keyword: str) -> list[dict]:
    """在标题和内容中搜索笔记"""
    logger.debug("[Store] search_notes | keyword=%s", keyword)
    notes = _load_json(NOTES_FILE)
    keyword_lower = keyword.lower()
    return [
        n for n in notes
        if keyword_lower in n["title"].lower()
        or keyword_lower in n["content"].lower()
    ]


# ──────────────────────────────────────
#  待办 (Todos) CRUD
# ──────────────────────────────────────

def create_todo(title: str, priority: str = "medium",
                due_date: Optional[str] = None) -> dict:
    """创建一条待办事项"""
    logger.debug("[Store] create_todo | title=%s, priority=%s, due_date=%s", title, priority, due_date)
    todos = _load_json(TODOS_FILE)
    todo = {
        "id": uuid.uuid4().hex[:8],
        "title": title,
        "done": False,
        "priority": priority,  # low / medium / high
        "due_date": due_date,
        "created_at": _now_iso(),
        "completed_at": None,
    }
    todos.append(todo)
    _save_json(TODOS_FILE, todos)
    return todo


def list_todos(status: Optional[str] = None,
               priority: Optional[str] = None) -> list[dict]:
    """列出待办，可按状态(done/pending)和优先级筛选"""
    logger.debug("[Store] list_todos | status=%s, priority=%s", status, priority)
    todos = _load_json(TODOS_FILE)
    if status == "done":
        todos = [t for t in todos if t["done"]]
    elif status == "pending":
        todos = [t for t in todos if not t["done"]]
    if priority:
        todos = [t for t in todos if t.get("priority") == priority]
    return todos


def complete_todo(todo_id: str) -> Optional[dict]:
    """标记待办为已完成"""
    logger.debug("[Store] complete_todo | todo_id=%s", todo_id)
    todos = _load_json(TODOS_FILE)
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = True
            t["completed_at"] = _now_iso()
            _save_json(TODOS_FILE, todos)
            return t
    return None


def delete_todo(todo_id: str) -> bool:
    """删除一条待办"""
    logger.debug("[Store] delete_todo | todo_id=%s", todo_id)
    todos = _load_json(TODOS_FILE)
    original_len = len(todos)
    todos = [t for t in todos if t["id"] != todo_id]
    if len(todos) < original_len:
        _save_json(TODOS_FILE, todos)
        return True
    return False


def get_summary() -> dict:
    """获取笔记和待办的整体统计摘要"""
    logger.debug("[Store] get_summary")
    notes = _load_json(NOTES_FILE)
    todos = _load_json(TODOS_FILE)
    pending = [t for t in todos if not t["done"]]
    done = [t for t in todos if t["done"]]
    high_priority = [t for t in pending if t.get("priority") == "high"]
    return {
        "total_notes": len(notes),
        "total_todos": len(todos),
        "pending_todos": len(pending),
        "completed_todos": len(done),
        "high_priority_pending": len(high_priority),
    }
