"""
主图编排
Phase 1: 定义 Agent 节点和它们之间的连接关系
Phase 2：在任务拆解前先检索知识库，注入到 Prompt 中
Phase 3：引入持久化 Checkpoint，支持多轮对话和回退
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
from state.agent_state import AgentState
from agents.intent_agent import IntentAgent
from agents.decompose_agent import DecomposeAgent
from agents.summary_agent import SummaryAgent
from rag.retrieve import KnowledgeRetriever



#全局检索器实例
retriever=KnowledgeRetriever()

#数据库文件路径
DB_PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),"data","checkpoints.db")

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
        print(f" 检索到 {len(results)} 条相关知识")

    return state


def should_retry(state:AgentState)->str:
    """如果用户最近一条消息表明不满意，返回 'decompose' 重新拆解"""
    last_msg=state["messages"][-1]
    content=last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    if any(word in content for word in ["不满意","不满","不满意","换一种","再来","重新"]):
        return "decompose" # 返回 'decompose'节点
    return "summary"

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
    # workflow.add_edge("summary",END)
    # phase 3 添加节点回滚从 summary 出来后，不是直接 END，而是根据条件决定是否重新拆解
    workflow.add_conditional_edges(
        "summary",
        should_retry,
        {
            "decompose": "decompose", # 回退到 任务拆解
            "summary": END  # 正常结束
        }
    )


    # 使用 SqliteSaver 持久化（3.x 需直接传 sqlite3.Connection）
    """
    langgraph-checkpoint-sqlite 3.x 把 from_conn_string 改成了上下文管理器（@contextmanager），
    直接调用返回的是 _GeneratorContextManager 而不是 SqliteSaver 实例，
    传给 workflow.compile() 会报错 Invalid checkpointer。改用 sqlite3.connect() 直接传连接对象，
    这是 3.x 推荐的初始化方式。
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    return workflow.compile(checkpointer=checkpointer)

#编译图，导出供main.py 使用
app=build_graph()