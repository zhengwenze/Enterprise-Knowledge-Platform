import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from src.agents.tools.base import BaseTool, ToolResult
from src.config import settings


@dataclass
class AgentStep:
    thought: str = ""
    action: str = ""
    action_input: Dict[str, Any] = field(default_factory=dict)
    observation: str = ""
    final_answer: str = ""


class ReActAgent:
    def __init__(self, tools: List[BaseTool], db_session=None):
        self.tools = {tool.name: tool for tool in tools}
        self.db_session = db_session
        self.conversation_history: List[Dict[str, str]] = []
        self.max_steps = 5

    def _get_tool_descriptions(self) -> str:
        descriptions = []
        for name, tool in self.tools.items():
            params = tool.parameters_schema.get("properties", {})
            required = tool.parameters_schema.get("required", [])
            param_desc = ", ".join(
                f"{k}{'(必需)' if k in required else '(可选)'}"
                for k in params.keys()
            )
            descriptions.append(f"- {name}: {tool.description} 参数: [{param_desc}]")
        return "\n".join(descriptions)

    def _build_prompt(self, question: str, history: List[AgentStep]) -> str:
        tool_descriptions = self._get_tool_descriptions()

        history_text = ""
        for i, step in enumerate(history, 1):
            if step.thought:
                history_text += f"\n步骤 {i}:\n"
                history_text += f"思考: {step.thought}\n"
            if step.action:
                history_text += f"行动: {step.action}\n"
                history_text += f"行动输入: {json.dumps(step.action_input, ensure_ascii=False)}\n"
            if step.observation:
                history_text += f"观察: {step.observation}\n"

        return f"""你是一个智能企业助手，可以使用以下工具来帮助用户解决问题。

可用工具:
{tool_descriptions}

使用 ReAct 格式回答问题。严格按照以下格式:

思考: 分析用户问题，决定下一步行动
行动: 工具名称(从可用工具中选择，或填写"最终答案")
行动输入: {{"参数名": "参数值"}}
观察: 工具返回结果
... (重复思考-行动-观察循环直到得出答案)
思考: 我现在知道最终答案了
行动: 最终答案
行动输入: {{"answer": "完整回答用户的问题"}}

重要规则:
1. 每次只能执行一个行动
2. 行动必须是可用工具之一或"最终答案"
3. 行动输入必须是有效的 JSON 格式
4. 如果问题可以直接回答，直接使用"最终答案"
5. 如果需要搜索知识库，使用 document_search 工具

历史对话:
{self._format_conversation_history()}

之前的步骤:
{history_text if history_text else "(无)"}

用户问题: {question}

思考:"""

    def _format_conversation_history(self) -> str:
        if not self.conversation_history:
            return "(无历史对话)"

        formatted = []
        for msg in self.conversation_history[-6:]:
            role = "用户" if msg["role"] == "user" else "助手"
            formatted.append(f"{role}: {msg['content'][:200]}")

        return "\n".join(formatted)

    def _parse_response(self, response: str) -> AgentStep:
        step = AgentStep()

        thought_match = re.search(r"思考[：:]\s*(.+?)(?=\n行动[：:]|$)", response, re.DOTALL)
        if thought_match:
            step.thought = thought_match.group(1).strip()

        action_match = re.search(r"行动[：:]\s*(.+?)(?=\n行动输入[：:]|$)", response)
        if action_match:
            step.action = action_match.group(1).strip()

        action_input_match = re.search(r"行动输入[：:]\s*(\{.+?\})", response, re.DOTALL)
        if action_input_match:
            try:
                step.action_input = json.loads(action_input_match.group(1))
            except json.JSONDecodeError:
                step.action_input = {}

        return step

    async def _call_llm(self, prompt: str) -> str:
        if settings.use_local_llm:
            return await self._call_ollama(prompt)
        else:
            return await self._call_openai(prompt)

    async def _call_ollama(self, prompt: str) -> str:
        import httpx

        messages = self.conversation_history + [{"role": "user", "content": prompt}]

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.local_llm_url}/api/chat",
                json={
                    "model": settings.llm_model,
                    "messages": messages,
                    "stream": False,
                },
            )
            result = response.json()
            return result.get("message", {}).get("content", "")

    async def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

        messages = self.conversation_history + [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content

    async def run(self, question: str) -> Dict[str, Any]:
        self.conversation_history.append({"role": "user", "content": question})

        history: List[AgentStep] = []
        final_answer = ""

        for step_num in range(self.max_steps):
            prompt = self._build_prompt(question, history)
            response = await self._call_llm(prompt)

            step = self._parse_response(response)
            history.append(step)

            if step.action == "最终答案" or step.action.lower() == "final_answer":
                final_answer = step.action_input.get("answer", step.observation)
                break

            if step.action in self.tools:
                tool = self.tools[step.action]
                result = await tool.execute(**step.action_input)
                step.observation = result.message

                if not result.success:
                    step.observation = f"工具执行失败: {result.message}"
            else:
                step.observation = f"未知工具: {step.action}。可用工具: {', '.join(self.tools.keys())}"

        if not final_answer:
            final_answer = "抱歉，我无法在限定步骤内完成任务。请尝试换一种方式提问。"

        self.conversation_history.append({"role": "assistant", "content": final_answer})

        return {
            "answer": final_answer,
            "steps": [
                {
                    "thought": s.thought,
                    "action": s.action,
                    "action_input": s.action_input,
                    "observation": s.observation,
                }
                for s in history
            ],
            "tools_used": list(set(s.action for s in history if s.action in self.tools)),
        }

    def clear_history(self):
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        return self.conversation_history.copy()
