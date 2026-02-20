from dataclasses import dataclass
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


@dataclass
class ToolResult:
    success: bool
    data: Any
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "message": self.message,
        }


class BaseTool(ABC):
    name: str = ""
    description: str = ""
    parameters_schema: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
        }
