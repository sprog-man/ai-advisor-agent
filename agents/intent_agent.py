"""
意图理解 Agent
把用户模糊的自然语言描述，转化为结构化的意图对象
"""
import json
from core.base_agent import BaseAgent
from core.llm_factory import call_llm
from state.agent_state import AgentState

class IntentAgent(BaseAgent):
    """负责理解用户意图，输出结构化描述"""
    def __init__(self):
        super().__init__(name="IntentAgent")

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
        self.log_start(state)

        try:
            # 使用兼容方法获取用户输入

            last_message_content = self._get_last_message_content(state)
            prompt=f"""你是一个AI领域的技术顾问。用户描述了一个想法或问题，请分析并返回一个JSON格式的结构化意图。

用户输入：{last_message_content}

返回格式（严格JSON，不要包含```json```标记或其他任何文字）：
{{
    "objective": "一句话概括用户想实现什么",
    "constraints": ["约束条件1", "约束条件2"],
    "domain": "所属AI子领域，如NLP、CV、推荐系统、LLM应用、模型部署等",
    "complexity": "simple|medium|complex"
}}

分析要求：
1. objective要抓住核心目标，不要啰嗦
2. constraints列出用户提到的限制条件，没有就写"无特殊限制"
3. domain要精确到AI具体子领域
4. complexity根据技术难度和涉及组件数量判断"""
            response=call_llm(prompt)

            # 解析JSON，处理可能的异常
            try:
                intent_data=json.loads(response)
            except json.JSONDecodeError:
                # 如果LLM返回了多余内容，尝试提取JSON部分
                content=response.strip()
                start=content.find("{")
                end=content.rfind("}")+1
                intent_data=json.loads(content[start:end])

            # 将结构化意图存入状态
            constraints_text="、".join(intent_data.get("constraints",["无特殊限制"]))
            state["user_intent"]=(
                f"目标：{intent_data['objective']}\n"
                f"领域：{intent_data.get('domain', 'AI通用')}\n"
                f"约束：{constraints_text}\n"
                f"复杂度：{intent_data.get('complexity', 'medium')}"
            )

            self.log_end(state)

        except Exception as e:
            self.log_error(e,state)
            # 出错时把原始输入作为意图，保证流程不中断
            state["user_intent"]=f"目标：{self._get_last_message_content(state)}\n领域：AI通用\n约束：无"
        debug_state = {k: v for k, v in state.items() if k != "messages"}
        print(f"[{self.name}] 输出预览:")
        print(json.dumps(debug_state, indent=2, ensure_ascii=False))

        return state
    
# 导出单例
intent_agent = IntentAgent()