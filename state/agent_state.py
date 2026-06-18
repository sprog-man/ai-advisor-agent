"""
Agent 全局状态定义
"""

from typing import TypedDict,List,Optional,Annotated,Any
from langgraph.graph.message import add_messages
from pydantic import BaseModel

class Task(BaseModel):
    """单个任务步骤"""
    id:int
    description:str
    dependencies:List[int]=[] # 依赖的任务ID列表
    status:str="pending"  # pending | in_progress | completed | failed
    result:Optional[str]=None  # 任务执行结果

class AgentState(TypedDict):
    """
    全局状态，贯穿整个 LangGraph 流水线
    
    字段说明：
    add_message 来自 LangGraph 的内置模块（第 6 行导入），它的作用是：每当这个字段被更新时，LangGraph 自动把新消息追加到列表末尾，而不是覆盖整个列表。
如果不加这个注解，新消息会把旧消息覆盖掉，对话历史就丢了。加了之后，LangGraph 会自动做 append 操作。
    - messages: 对话历史（LangGraph 使用 add_messages 自动合并）
    - user_intent: 结构化后的用户意图
    - plan: 任务拆解后的步骤列表
    - knowledge_context: 从RAG检索到的知识片段
    - final_summary: 最终返回给用户的总结
    - error_count: 当前步骤的重试次数
    - max_retries: 最大重试次数
    - current_checkpoint_id: 当前检查点ID
    - status: 整体流程状态 running | success | failed | paused
    """
    messages: Annotated[List[dict],add_messages]
    user_intent:str
    plan:List[dict]
    knowledge_context:str
    final_summary:str
    error_count:int
    max_retries:int
    current_checkpoint_id:Optional[str]
    status:str
    long_term_context:str
    extracted_memory:dict

