"""
记忆提炼 Agent
从对话中提取用户偏好和关键事实，用于写入长期记忆
"""

from core.base_agent import BaseAgent
from core.llm_factory import create_llm
from state.agent_state import AgentState
from state.schemas import MemoryExtraction

class MemoryExtractionAgents(BaseAgent):
    def __init__(self):
        super().__init__(name="MemoryExtractionAgent")
        self.structured_llm=create_llm(temperature=0.5).with_structured_output(MemoryExtraction)

    def __call__(self,state:AgentState)->AgentState:
        self.log_start(state)
        try:
            # 用最近的几条消息来提炼
            recent=state["messages"][-6:]  #取最新6条消息
            dialogue="\n".join(
                f"{'用户' if m.type=='human' else 'AI'}:{m.content}"
                for m in recent if hasattr(m,"type") and hasattr(m,"content")
            )
            extraction:MemoryExtraction=self.structured_llm.invoke(
                f"你是一个记忆会话提取专家，请根据提供的会话记录中提取用户偏好和重要事实：\n{dialogue}"
            )
            # 存入状态,供后续manager记录
            state["extracted_memory"]=extraction.dict()
            self.log_end(state)

        except Exception as e:
            self.log_error(e,state)
            state["extracted_memory"]={}
        return state
    
memory_extraction_agent=MemoryExtractionAgents()
            
            