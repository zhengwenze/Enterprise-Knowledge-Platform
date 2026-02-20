# EKP Agent 升级路线图

## 背景

根据 AI 行业趋势，2026 年主战场是 Agent 和 AI Native App。EKP 需要从简单的 RAG 问答系统升级为智能 Agent 平台。

## 当前状态 vs 目标状态

| 维度 | 当前 | 目标 |
|------|------|------|
| 架构 | RAG 问答 | Agent + RAG |
| 对话 | 单轮 | 多轮 + 记忆 |
| 能力 | 文档检索 | 工具调用 + 自主决策 |
| 交互 | 被动响应 | 主动建议 |

## Phase 1: ReAct Agent 基础架构

### 1.1 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    ReAct Agent                          │
├─────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Reason  │ →  │  Act    │ →  │ Observe │            │
│  │ (思考)  │    │ (行动)  │    │ (观察)  │            │
│  └─────────┘    └─────────┘    └─────────┘            │
│       ↓              ↓              ↓                   │
│  理解用户意图    选择工具执行    分析结果              │
└─────────────────────────────────────────────────────────┘
```

### 1.2 工具定义

```python
# src/agents/tools/__init__.py

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ToolResult:
    success: bool
    data: Any
    message: str

class BaseTool(ABC):
    name: str
    description: str
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

class DocumentSearchTool(BaseTool):
    name = "document_search"
    description = "搜索企业知识库文档，获取相关信息"
    
    def __init__(self, rag_service):
        self.rag = rag_service
    
    async def execute(self, query: str, top_k: int = 5) -> ToolResult:
        result = await self.rag.query(query, mode="hybrid")
        return ToolResult(success=True, data=result, message="搜索完成")

class DocumentUploadTool(BaseTool):
    name = "document_upload"
    description = "上传文档到知识库"
    
    async def execute(self, file_path: str) -> ToolResult:
        # 实现文档上传逻辑
        pass

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "搜索互联网获取最新信息"
    
    async def execute(self, query: str) -> ToolResult:
        # 可选：集成搜索API
        pass

class DatabaseQueryTool(BaseTool):
    name = "database_query"
    description = "查询企业数据库"
    
    async def execute(self, sql: str) -> ToolResult:
        # 安全的SQL查询执行
        pass
```

### 1.3 ReAct Agent 实现

```python
# src/agents/react_agent.py

import json
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class AgentStep:
    thought: str
    action: str
    action_input: dict
    observation: str

class ReActAgent:
    def __init__(self, llm_client, tools: List[BaseTool]):
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in tools}
        self.memory = []
    
    def _build_prompt(self, question: str, history: List[AgentStep]) -> str:
        tool_descriptions = "\n".join([
            f"- {name}: {tool.description}" 
            for name, tool in self.tools.items()
        ])
        
        history_text = ""
        for step in history:
            history_text += f"""
思考: {step.thought}
行动: {step.action}
行动输入: {json.dumps(step.action_input)}
观察: {step.observation}
"""
        
        return f"""你是一个智能企业助手，可以使用以下工具：

{tool_descriptions}

使用以下格式回答：

思考: 分析用户问题，决定下一步行动
行动: 工具名称（从上述工具中选择）
行动输入: 工具参数（JSON格式）
观察: 工具返回结果
... (重复思考-行动-观察循环直到得出答案)
思考: 我现在知道最终答案了
最终答案: 对用户问题的完整回答

历史对话：
{history_text}

用户问题: {question}

思考:"""

    async def run(self, question: str, max_steps: int = 5) -> str:
        history = []
        
        for _ in range(max_steps):
            prompt = self._build_prompt(question, history)
            response = await self.llm.generate(prompt)
            
            # 解析响应
            step = self._parse_response(response)
            
            if step.action == "最终答案":
                return step.observation
            
            # 执行工具
            if step.action in self.tools:
                tool = self.tools[step.action]
                result = await tool.execute(**step.action_input)
                step.observation = result.message
            
            history.append(step)
        
        return "抱歉，我无法在限定步骤内完成任务。"

    def _parse_response(self, response: str) -> AgentStep:
        # 解析 LLM 响应
        pass
```

## Phase 2: 记忆系统

### 2.1 记忆类型

```python
# src/agents/memory.py

from typing import List, Dict
from datetime import datetime

class MemorySystem:
    def __init__(self, db_session):
        self.db = db_session
    
    async def save_conversation(
        self, 
        user_id: int,
        session_id: str,
        messages: List[Dict]
    ):
        """保存对话历史"""
        pass
    
    async def get_relevant_history(
        self,
        user_id: int,
        current_query: str,
        limit: int = 5
    ) -> List[Dict]:
        """获取相关历史对话"""
        pass
    
    async def save_user_preference(
        self,
        user_id: int,
        key: str,
        value: str
    ):
        """保存用户偏好"""
        pass
    
    async def get_user_context(self, user_id: int) -> Dict:
        """获取用户上下文（偏好、历史等）"""
        pass
```

### 2.2 记忆层次

| 类型 | 说明 | 存储 |
|------|------|------|
| 工作记忆 | 当前对话上下文 | Redis |
| 短期记忆 | 最近 N 轮对话 | PostgreSQL |
| 长期记忆 | 用户偏好、知识 | PostgreSQL + 向量 |
| 知识记忆 | 企业文档知识 | RAG 向量库 |

## Phase 3: Multi-Agent 协作

### 3.1 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                     │
│                    (任务分发协调)                        │
└─────────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ HR Agent    │ │ IT Agent    │ │ Finance     │
│ (人事助手)  │ │ (IT助手)    │ │ Agent       │
└─────────────┘ └─────────────┘ └─────────────┘
         │              │              │
         └──────────────┼──────────────┘
                        ▼
              ┌─────────────────┐
              │  Shared Tools   │
              │  (共享工具层)   │
              └─────────────────┘
```

### 3.2 专业 Agent 定义

```python
# src/agents/specialized/__init__.py

class HRAgent:
    """人事助手 - 处理请假、报销、入职等问题"""
    tools = ["document_search", "database_query", "email_send"]
    system_prompt = "你是企业人事助手，擅长处理人事相关问题..."

class ITAgent:
    """IT助手 - 处理技术支持、系统问题"""
    tools = ["document_search", "ticket_create", "system_check"]
    system_prompt = "你是企业IT助手，擅长解决技术问题..."

class FinanceAgent:
    """财务助手 - 处理报销、预算等问题"""
    tools = ["document_search", "database_query", "approval_workflow"]
    system_prompt = "你是企业财务助手，擅长处理财务相关问题..."
```

## Phase 4: AI Native 体验优化

### 4.1 主动建议

```python
# 用户上传文档后，Agent 主动分析并建议
async def analyze_and_suggest(document_id: int):
    # 1. 分析文档内容
    # 2. 识别关键信息
    # 3. 生成主动建议
    suggestions = [
        "这份文档涉及信息安全，建议添加到安全培训材料",
        "发现3处过时政策，建议更新",
        "相关文档：公司行为准则、数据安全规范"
    ]
    return suggestions
```

### 4.2 智能推荐

```python
# 基于用户行为推荐相关内容
async def smart_recommend(user_id: int, context: dict):
    # 分析用户历史查询
    # 推荐可能感兴趣的内容
    # 推荐可能需要的文档
    pass
```

## 实施时间线

| 阶段 | 内容 | 时间 |
|------|------|------|
| Phase 1 | ReAct Agent 基础 | 2 周 |
| Phase 2 | 记忆系统 | 1 周 |
| Phase 3 | Multi-Agent | 2 周 |
| Phase 4 | AI Native 体验 | 1 周 |

## 技术选型建议

| 组件 | 推荐方案 | 原因 |
|------|---------|------|
| Agent 框架 | LangChain / 自研 | 灵活可控 |
| LLM | Ollama (本地) | 成本低、隐私安全 |
| 向量库 | pgvector | 已集成 |
| 记忆存储 | Redis + PostgreSQL | 高性能 + 持久化 |
| 工具调用 | 自定义 Tool 类 | 业务定制 |

## 预期效果

| 指标 | 当前 | 升级后 |
|------|------|--------|
| 问答准确率 | 70% | 90%+ |
| 用户满意度 | 中 | 高 |
| 功能丰富度 | 单一问答 | 多工具协作 |
| 企业价值 | 知识检索 | 智能助手 |
