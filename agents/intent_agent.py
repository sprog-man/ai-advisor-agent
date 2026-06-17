"""
意图理解 Agent
把用户模糊的自然语言描述，转化为结构化的意图对象
"""
import json
from core.base_agent import BaseAgent
from core.llm_factory import create_llm
from state.agent_state import AgentState
from state.schemas import IntentSchema

class IntentAgent(BaseAgent):
    """负责理解用户意图，输出结构化描述"""
    def __init__(self):
        super().__init__(name="IntentAgent")
        self.structured_llm = create_llm(temperature=0.5).with_structured_output(IntentSchema)


    # phase3 新增上下文窗口阈值设定
    def _compress_history_if_needed(self, state: AgentState, max_messages: int = 20):
        messages = state["messages"]
        if len(messages) <= max_messages:
            return state
        
        # 保留最近 20 条原始消息，其余生成摘要
        """"
        [:-20] — 从开头到倒数第 20 条（不包含），即"前 N-20 条"
        [-20:] — 从倒数第 20 条到末尾，即"最近 20 条"
        """
        old_messages = messages[:-max_messages]
        recent=messages[-max_messages:]

        # 用 LLM 总结旧对话
        old_text="\n".join(
            f"{'用户' if m.type== 'human' else '助手'}: {m.content}"
            for m in old_messages if hasattr(m, "type") and hasattr(m, "content")
        )

        summary_prompt = f"你是一个会话总结专家，请分析旧会话的信息，将其以凝练的语句将总结成一段简短摘：\n{old_text}"
        summary=create_llm(temperature=0.3).invoke(summary_prompt).content
        # 把旧消息替换成一句摘要 + 保留最近的
        state["messages"]=[
            {
                "type": "system",
                "content": f"历史对话摘要：{summary}"
            }
        ] + recent

    def _get_last_message_content(self,state:AgentState)->str:
        """兼容获取最后一条消息的内容，同时支持 dict 和 LangChain Message 对象"""
        last_message=state["messages"][-1]

        # LangChain Message 对象 (HumanMessage, AIMessage 等)
        if hasattr(last_message, "content"):
            return last_message.content
        
        #普通字典
        if isinstance(last_message, dict):
            return last_message.get("content", "")
        
        #兜底：直接转字符串
        return str(last_message)
    
    def __call__(self,state:AgentState)->AgentState:
        state=self._compress_history_if_needed(state) #phase3 新增
        self.log_start(state)

        # try:
            # 最初的方法一，没有使用schemas规范结构
#             # 使用兼容方法获取用户输入

#             last_message_content = self._get_last_message_content(state)
#             prompt=f"""你是一个AI领域的技术顾问。用户描述了一个想法或问题，请分析并返回一个JSON格式的结构化意图。

# 用户输入：{last_message_content}

# 返回格式（严格JSON，不要包含```json```标记或其他任何文字）：
# {{
#     "objective": "一句话概括用户想实现什么",
#     "constraints": ["约束条件1", "约束条件2"],
#     "domain": "所属AI子领域，如NLP、CV、推荐系统、LLM应用、模型部署等",
#     "complexity": "simple|medium|complex"
# }}

# 分析要求：
# 1. objective要抓住核心目标，不要啰嗦
# 2. constraints列出用户提到的限制条件，没有就写"无特殊限制"
# 3. domain要精确到AI具体子领域
# 4. complexity根据技术难度和涉及组件数量判断"""
#             response=call_llm(prompt)

#             # 解析JSON，处理可能的异常
#             try:
#                 intent_data=json.loads(response)
#             except json.JSONDecodeError:
#                 # 如果LLM返回了多余内容，尝试提取JSON部分
#                 content=response.strip()
#                 start=content.find("{")
#                 end=content.rfind("}")+1
#                 intent_data=json.loads(content[start:end])

#             # 将结构化意图存入状态
#             constraints_text="、".join(intent_data.get("constraints",["无特殊限制"]))
#             state["user_intent"]=(
#                 f"目标：{intent_data['objective']}\n"
#                 f"领域：{intent_data.get('domain', 'AI通用')}\n"
#                 f"约束：{constraints_text}\n"
#                 f"复杂度：{intent_data.get('complexity', 'medium')}"
#             )

        # 最初的方法二，使用schemas规范结构
        try:
            user_input=self._get_last_message_content(state)
            prompt = f"""你是一个AI技术领域的意图理解专家。分析用户的输入，提取关键信息。

用户输入：{user_input}

请用一句话概括用户想了解什么或实现什么（用自然语言描述，不要用分类标签）。"""
            intent:IntentSchema=self.structured_llm.invoke(prompt)

            constraints_text="、".join(intent.constraints) if intent.constraints else "无特殊限制"
            state["user_intent"]=(
                f"目标：{intent.objective}\n"
                f"领域：{intent.domain}\n"
                f"约束：{constraints_text}\n"
                f"复杂度：{intent.complexity}"
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log_error(e,state)
            fallback_content=self._get_last_message_content(state)
            state["user_intent"]=f"目标：{fallback_content}\n领域：AI通用\n约束：无"

        return state
    
# 导出单例
intent_agent = IntentAgent()