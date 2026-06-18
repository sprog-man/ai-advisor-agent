"""
记忆管理器
统一温记忆的写入、检索和融合
"""

from typing import List
from langchain_core.documents import Document
from .vector_store import WarmVectorMemory
from .knowledge_graph import WarmKnowledgeGraph
from .cold_store import ColdLogStore
from state.schemas import KeyFact, MemoryExtraction,UserPreference

class MemoryManager:
    def __init__(self):
        self.vector=WarmVectorMemory()
        self.graph=WarmKnowledgeGraph()
        self.cold_store=ColdLogStore()

    def record_extraction(self,extraction:MemoryExtraction,thread_id:str=None):
        # 写向量库
        for pref in extraction.preferences:
            text=f"偏好：{pref.category}->{pref.value}"
            self.vector.add_memory(text,{"type":"preference",**pref.dict()})
        for fact in extraction.facts:
            text=f"事实：{fact.subject} {fact.predicate} {fact.object}"
            self.vector.add_memory(text,{"type":"fact",**fact.dict()})
            self.graph.add_triple(fact.subject,fact.predicate,fact.object,{"confidence":fact.confidence})
        
    def retrieve(self,query:str,top_k=3):
        # 向量检索记录
        vec_doc=self.vector.search(query,top_k)
        return {"vector":vec_doc,"graph":[]}   #graph 待实现（可扩展）
    
    def format_results(self,retrieval_result):
        """
        格式化上面retrieve的检索结果
        """

        parts=[f"-{d.page_content}" for d in retrieval_result["vector"]]
        return "\n".join(parts) if parts else "暂无相关长期记忆"
    
    


