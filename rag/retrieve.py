"""
检索器
负责文档向量化和语义搜索
"""

import os
from typing import List,Optional
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from config.settings import settings

class KnowledgeRetriever:
    """知识库检索器，封装向量存储和查询"""

    def __init__(self,collection_name: str = "ai_knowledge"):
        """
        Args:
            collection_name: ChromaDB 集合名称
        """
        self.collection_name = collection_name
        self.embeddings=OpenAIEmbeddings(
            api_key=settings.embedding.api_key,
            base_url=settings.embedding.base_url,
            model=settings.embedding.model,
            check_embedding_ctx_length=False,
            chunk_size=10
        )
        self.vector_store:Optional[Chroma] = None
        self._init_vector_store()

    def _init_vector_store(self):
        """初始化或加载向量库"""
        chroma_dir=os.path.join(settings.chroma_db_dir,self.collection_name)
        os.makedirs(chroma_dir,exist_ok=True)

        self.vector_store=Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=chroma_dir
        )

    def add_documents(self,documents:List[Document]):
        """
        将文档块添加到向量库
        
        Args:
            documents: 分块后的文档列表
        """
        if not documents:
            print("⚠️ 没有文档需要添加")
            return
        
        self.vector_store.add_documents(documents)
        print(f"✅ 已将 {len(documents)} 个文档块存入向量库")

    def search(self,query:str,top_k:int=5)->List[Document]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            top_k: 返回的最相关文档数
        
        Returns:
            最相关的文档块列表
        """
        if self.vector_store is None:
            print("⚠️ 向量库未初始化")
            return []
        
        results = self.vector_store.similarity_search(query, k=top_k)
        return results
    
    def format_results(self,results:List[Document])->str:
        """
        将检索结果格式化为可注入Prompt的文本
        
        Args:
            results: 检索到的文档列表
        
        Returns:
            格式化后的文本
        """

        if not results:
            return "未找到相关知识。"
        
        formatted_parts=[]
        for i,doc in enumerate(results,1):
            source=doc.metadata.get("source","未知来源")
            file_type=doc.metadata.get("file_type","")

            header=f"【参考资料{i}】来源：{source}（{file_type}）"
            formatted_parts.append(f"{header}\n{doc.page_content}\n")

        return "\n\n"+"\n\n".join(formatted_parts)
    
    

    


    





