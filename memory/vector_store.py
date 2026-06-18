"""
温记忆-向量存储
存储用户偏好、关键事实的向量化记忆，支持语义联想
"""

from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from config.settings import settings
import os

class WarmVectorMemory:
    def __init__(self,collection_name:str="user_memory"):
        self.collection_name=collection_name
        self.embeddings=OpenAIEmbeddings(
            api_key=settings.embedding.api_key,
            base_url=settings.embedding.base_url,
            model=settings.embedding.model,
        )

        persist_dir=os.path.join(settings.chroma_db_dir,collection_name)
        self.store=Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_dir,
        )

    def add_memory(self,content:str,metadata:dict):
        """添加一条记忆"""
        doc=Document(page_content=content,metadata=metadata)
        self.store.add_documents([doc])

    def search(self,query:str,top_k:int=5)->List[Document]:
        return self.store.similarity_search(query,k=top_k)
    
    def delete(self,doc_id:str):
        self.store.delete(ids=[doc_id])