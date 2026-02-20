from typing import Any, Dict

from src.agents.tools.base import BaseTool, ToolResult
from src.services.rag_anything_service import rag_anything_service


class DocumentSearchTool(BaseTool):
    name = "document_search"
    description = "搜索企业知识库文档，获取相关信息。当用户询问公司政策、流程、规定等问题时使用此工具。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索查询，用户的问题或关键词",
            },
            "mode": {
                "type": "string",
                "description": "检索模式: hybrid(混合), local(本地), global(全局)",
                "default": "hybrid",
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, mode: str = "hybrid", **kwargs) -> ToolResult:
        try:
            result = await rag_anything_service.query(
                question=query,
                mode=mode,
            )
            return ToolResult(
                success=True,
                data={"answer": result},
                message="搜索完成",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"搜索失败: {str(e)}",
            )


class DocumentUploadTool(BaseTool):
    name = "document_upload"
    description = "上传文档到知识库。支持 PDF、Word、TXT、Markdown 等格式。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文档文件路径",
            },
        },
        "required": ["file_path"],
    }

    async def execute(self, file_path: str, **kwargs) -> ToolResult:
        try:
            result = await rag_anything_service.process_document(file_path=file_path)
            if result.get("status") == "success":
                return ToolResult(
                    success=True,
                    data=result,
                    message="文档上传并处理成功",
                )
            else:
                return ToolResult(
                    success=False,
                    data=result,
                    message=result.get("error", "文档处理失败"),
                )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"上传失败: {str(e)}",
            )


class DocumentListTool(BaseTool):
    name = "document_list"
    description = "获取知识库中的文档列表。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "返回文档数量限制",
                "default": 10,
            },
        },
    }

    def __init__(self, db_session):
        self.db = db_session

    async def execute(self, limit: int = 10, **kwargs) -> ToolResult:
        try:
            from src.models.document import Document

            documents = (
                self.db.query(Document)
                .order_by(Document.created_at.desc())
                .limit(limit)
                .all()
            )

            doc_list = [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "status": doc.status,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                }
                for doc in documents
            ]

            return ToolResult(
                success=True,
                data={"documents": doc_list, "count": len(doc_list)},
                message=f"获取到 {len(doc_list)} 个文档",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"获取文档列表失败: {str(e)}",
            )


class CalculatorTool(BaseTool):
    name = "calculator"
    description = "执行数学计算。用于计算数字、百分比等。"
    parameters_schema = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 '2+2', '100*0.15', '(10+5)*2'",
            },
        },
        "required": ["expression"],
    }

    async def execute(self, expression: str, **kwargs) -> ToolResult:
        try:
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return ToolResult(
                    success=False,
                    data=None,
                    message="表达式包含不允许的字符",
                )

            result = eval(expression)
            return ToolResult(
                success=True,
                data={"expression": expression, "result": result},
                message=f"计算结果: {result}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                message=f"计算失败: {str(e)}",
            )


class CurrentTimeTool(BaseTool):
    name = "current_time"
    description = "获取当前日期和时间。"
    parameters_schema = {
        "type": "object",
        "properties": {},
    }

    async def execute(self, **kwargs) -> ToolResult:
        from datetime import datetime

        now = datetime.now()
        return ToolResult(
            success=True,
            data={
                "datetime": now.isoformat(),
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "weekday": now.strftime("%A"),
            },
            message=f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}",
        )
