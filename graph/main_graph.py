"""
主图编排
Phase 1: 定义 Agent 节点和它们之间的连接关系
Phase 2：在任务拆解前先检索知识库，注入到 Prompt 中
"""

from langgraph.graph import StateGraph, END
from state.agent_state import AgentState
from agents.intent_agent import IntentAgent
from agents.decompose_agent import DecomposeAgent
from agents.summary_agent import SummaryAgent
from rag.retrieve import KnowledgeRetriever



#全局检索器实例
retriever=KnowledgeRetriever()

def retrieve_knowledge(state:AgentState)->AgentState:
    """
    知识检索节点：
    根据用户意图从知识库中检索相关内容，存入 state["knowledge_context"]
    """
    query=state.get("user_intent","")

    if not query:
        state["knowledge_context"]=""
        return state
    
    # 检索相关文档
    results=retriever.search(query,top_k=5)

    #格式化并存入状态
    state["knowledge_context"]=retriever.format_results(results)

    if results:
        print(f"📖 检索到 {len(results)} 条相关知识")

    return state



def build_graph():
    
    """构建并返回编译后的LangGraph"""

    #创建状态图
    workflow=StateGraph(AgentState)

    #注册节点
    workflow.add_node("intent",IntentAgent())
    workflow.add_node("retrieve",retrieve_knowledge) #Phase 2 新增
    workflow.add_node("decompose",DecomposeAgent())
    workflow.add_node("summary",SummaryAgent())

    #设置入口
    workflow.set_entry_point("intent")

    #连线：线性流水线
    # 连线：意图理解 → 知识检索 → 任务拆解 → 总结
    workflow.add_edge("intent","retrieve")
    workflow.add_edge("retrieve","decompose")
    workflow.add_edge("decompose","summary")
    workflow.add_edge("summary",END)

    return workflow.compile()

#编译图，导出供main.py 使用
app=build_graph()