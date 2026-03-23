"""
Notes & Todo MCP Server
提供笔记管理和待办管理两大类工具，数据存储在本地 JSON 文件中。
"""

import json
import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from notes_todo_mcp import store

# 配置日志输出到 stderr，避免污染 stdout（MCP 使用 stdout 通信）
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# 创建 MCP Server 实例
mcp = FastMCP(
    "Notes & Todo",
    instructions="本地笔记与待办事项管理 MCP Server",
)


# ──────────────────────────────────────────────
#  笔记相关 Tools
# ──────────────────────────────────────────────

@mcp.tool()
def create_note(title: str, content: str, tags: list[str] | None = None) -> str:
    """创建一条新笔记。

    Args:
        title: 笔记标题
        content: 笔记正文内容
        tags: 可选的标签列表，用于分类，如 ["工作", "灵感"]
    """
    logger.debug("[MCP调用] create_note | title=%s, tags=%s", title, tags)
    note = store.create_note(title, content, tags)
    return json.dumps(note, ensure_ascii=False, indent=2)


@mcp.tool()
def list_notes(tag: str | None = None) -> str:
    """列出所有笔记，可按标签筛选。

    Args:
        tag: 可选，按此标签筛选笔记
    """
    logger.debug("[MCP调用] list_notes | tag=%s", tag)
    notes = store.list_notes(tag)
    if not notes:
        return "当前没有笔记。"
    lines = []
    for n in notes:
        tags_str = ", ".join(n["tags"]) if n["tags"] else "无"
        lines.append(
            f"• [{n['id']}] {n['title']}  (标签: {tags_str} | 更新于: {n['updated_at'][:10]})"
        )
    return "\n".join(lines)


@mcp.tool()
def get_note(note_id: str) -> str:
    """根据 ID 查看笔记的完整内容。

    Args:
        note_id: 笔记 ID
    """
    logger.debug("[MCP调用] get_note | note_id=%s", note_id)
    note = store.get_note(note_id)
    if note is None:
        return f"未找到 ID 为 {note_id} 的笔记。"
    return json.dumps(note, ensure_ascii=False, indent=2)


@mcp.tool()
def update_note(
    note_id: str,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
) -> str:
    """更新一条已有笔记的标题、内容或标签。

    Args:
        note_id: 要更新的笔记 ID
        title: 新标题（留空则不改）
        content: 新内容（留空则不改）
        tags: 新标签列表（留空则不改）
    """
    logger.debug("[MCP调用] update_note | note_id=%s", note_id)
    note = store.update_note(note_id, title, content, tags)
    if note is None:
        return f"未找到 ID 为 {note_id} 的笔记。"
    return f"笔记已更新：\n{json.dumps(note, ensure_ascii=False, indent=2)}"


@mcp.tool()
def delete_note(note_id: str) -> str:
    """删除一条笔记。

    Args:
        note_id: 要删除的笔记 ID
    """
    logger.debug("[MCP调用] delete_note | note_id=%s", note_id)
    ok = store.delete_note(note_id)
    return f"笔记 {note_id} 已删除。" if ok else f"未找到 ID 为 {note_id} 的笔记。"


@mcp.tool()
def search_notes(keyword: str) -> str:
    """根据关键词搜索笔记（匹配标题和内容）。

    Args:
        keyword: 搜索关键词
    """
    logger.debug("[MCP调用] search_notes | keyword=%s", keyword)
    results = store.search_notes(keyword)
    if not results:
        return f"未找到包含「{keyword}」的笔记。"
    lines = [f"找到 {len(results)} 条匹配笔记："]
    for n in results:
        lines.append(f"• [{n['id']}] {n['title']}")
    return "\n".join(lines)


# ──────────────────────────────────────────────
#  待办相关 Tools
# ──────────────────────────────────────────────

@mcp.tool()
def create_todo(
    title: str,
    priority: str = "medium",
    due_date: str | None = None,
) -> str:
    """创建一条待办事项。

    Args:
        title: 待办事项描述
        priority: 优先级，可选 low / medium / high，默认 medium
        due_date: 可选的截止日期，格式如 2025-12-31
    """
    logger.debug("[MCP调用] create_todo | title=%s, priority=%s, due_date=%s", title, priority, due_date)
    todo = store.create_todo(title, priority, due_date)
    return json.dumps(todo, ensure_ascii=False, indent=2)


@mcp.tool()
def list_todos(status: str | None = None, priority: str | None = None) -> str:
    """列出待办事项，可按状态和优先级筛选。

    Args:
        status: 可选，done（已完成）或 pending（未完成）
        priority: 可选，按优先级筛选 low / medium / high
    """
    logger.debug("[MCP调用] list_todos | status=%s, priority=%s", status, priority)
    todos = store.list_todos(status, priority)
    if not todos:
        return "当前没有待办事项。"

    priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    lines = []
    for t in todos:
        check = "✅" if t["done"] else "⬜"
        emoji = priority_emoji.get(t.get("priority", "medium"), "🟡")
        due = f" (截止: {t['due_date']})" if t.get("due_date") else ""
        lines.append(f"{check} {emoji} [{t['id']}] {t['title']}{due}")
    return "\n".join(lines)


@mcp.tool()
def complete_todo(todo_id: str) -> str:
    """将一条待办标记为已完成。

    Args:
        todo_id: 待办 ID
    """
    logger.debug("[MCP调用] complete_todo | todo_id=%s", todo_id)
    todo = store.complete_todo(todo_id)
    if todo is None:
        return f"未找到 ID 为 {todo_id} 的待办。"
    return f"✅ 已完成：{todo['title']}"


@mcp.tool()
def delete_todo(todo_id: str) -> str:
    """删除一条待办事项。

    Args:
        todo_id: 要删除的待办 ID
    """
    logger.debug("[MCP调用] delete_todo | todo_id=%s", todo_id)
    ok = store.delete_todo(todo_id)
    return f"待办 {todo_id} 已删除。" if ok else f"未找到 ID 为 {todo_id} 的待办。"


# ──────────────────────────────────────────────
#  综合工具
# ──────────────────────────────────────────────

@mcp.tool()
def get_summary() -> str:
    """获取笔记和待办的整体统计摘要。"""
    logger.debug("[MCP调用] get_summary")
    s = store.get_summary()
    return (
        f"📊 数据概览\n"
        f"─────────────────\n"
        f"📝 笔记总数：{s['total_notes']}\n"
        f"📋 待办总数：{s['total_todos']}\n"
        f"  ⬜ 待完成：{s['pending_todos']}\n"
        f"  ✅ 已完成：{s['completed_todos']}\n"
        f"  🔴 高优先级未完成：{s['high_priority_pending']}"
    )


# ──────────────────────────────────────────────
#  MCP Resources（让 AI 能直接读取数据）
# ──────────────────────────────────────────────

@mcp.resource("notes://all")
def all_notes_resource() -> str:
    """获取所有笔记的完整数据"""
    logger.debug("[MCP调用] resource: notes://all")
    notes = store.list_notes()
    return json.dumps(notes, ensure_ascii=False, indent=2)


@mcp.resource("todos://all")
def all_todos_resource() -> str:
    """获取所有待办的完整数据"""
    logger.debug("[MCP调用] resource: todos://all")
    todos = store.list_todos()
    return json.dumps(todos, ensure_ascii=False, indent=2)


@mcp.resource("summary://overview")
def summary_resource() -> str:
    """获取统计摘要"""
    logger.debug("[MCP调用] resource: summary://overview")
    return json.dumps(store.get_summary(), ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────
#  入口
# ──────────────────────────────────────────────

def main():
    mcp.run()


if __name__ == "__main__":
    main()
