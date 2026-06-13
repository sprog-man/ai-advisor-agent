"""
主图编排
定义 Agent 节点和它们之间的连接关系
"""

from langgraph.graph import StateGraph, END
from state.agent_state import AgentState
from agents.intent_agent import IntentAgent
from agents.decompose_agent import DecomposeAgent
from agents.summary_agent import SummaryAgent

def build_graph():
    
    """构建并返回编译后的LangGraph"""

    #创建状态图
    workflow=StateGraph(AgentState)

    #注册节点
    workflow.add_node("intent",IntentAgent())
    workflow.add_node("decompose",DecomposeAgent())
    workflow.add_node("summary",SummaryAgent())

    #设置入口
    workflow.set_entry_point("intent")

    #连线：线性流水线
    workflow.add_edge("intent","decompose")
    workflow.add_edge("decompose","summary")
    workflow.add_edge("summary",END)

    return workflow.compile()

#编译图，导出供main.py 使用
app=build_graph()