# 📝 Notes & Todo MCP Server

一个本地笔记与待办事项管理的 MCP Server，数据以 JSON 文件形式存储在本地。

## 功能列表

### 笔记管理
| 工具 | 说明 |
|------|------|
| `create_note` | 创建笔记（支持标签分类） |
| `list_notes` | 列出所有笔记（可按标签筛选） |
| `get_note` | 查看笔记详情 |
| `update_note` | 更新笔记内容 |
| `delete_note` | 删除笔记 |
| `search_notes` | 关键词搜索笔记 |

### 待办管理
| 工具 | 说明 |
|------|------|
| `create_todo` | 创建待办（支持优先级和截止日期） |
| `list_todos` | 列出待办（可按状态/优先级筛选） |
| `complete_todo` | 标记待办为已完成 |
| `delete_todo` | 删除待办 |

### 综合
| 工具 | 说明 |
|------|------|
| `get_summary` | 统计摘要（笔记/待办数量概览） |

## 安装

```bash
cd /path/to/mcp_demo
pip install -e .
```

## 运行

```bash
# 直接运行
notes-todo-mcp

# 或者用 Python 运行
python -m notes_todo_mcp.server
```

## 在 MCP 客户端中配置

将以下配置添加到你的 MCP 客户端配置文件中：

```json
{
  "mcpServers": {
    "notes-todo": {
      "command": "python",
      "args": ["-m", "notes_todo_mcp.server"],
      "cwd": "/path/to/mcp_demo"
    }
  }
}
```

## 数据存储

所有数据保存在 `~/.notes-todo-mcp/` 目录下：
- `notes.json` — 笔记数据
- `todos.json` — 待办数据

## 项目结构

```
mcp_demo/
├── pyproject.toml              # 项目配置
├── README.md                   # 说明文档
└── notes_todo_mcp/
    ├── __init__.py
    ├── server.py               # MCP Server 主入口，Tools & Resources 注册
    └── store.py                # 本地 JSON 存储层
```
