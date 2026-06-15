"""
文档入库脚本
将 knowledge_base 目录下的所有文档加载、分块、向量化并存入 ChromaDB
"""

import sys
import os

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from rag.document_loader import DocumentLoader
from rag.text_splitter import SmartTextSplitter
from rag.retrieve import KnowledgeRetriever

def main():
    print("=" * 60)
    print("📚 知识库文档入库")
    print("=" * 60)
    print(f"知识库目录：{settings.knowledge_base_dir}")
    print(f"向量库目录：{settings.chroma_db_dir}")
    print()

    # 1. 加载文档
    print("【步骤1】加载文档...")
    loader = DocumentLoader(settings.knowledge_base_dir)
    documents = loader.load_all()

    if not documents:
        print("没有找到文档，请检查知识库目录是否正确")
        return
    
    #2.分块
    print("\n【步骤2】智能分块...")
    splitter=SmartTextSplitter(chunk_size=1000,chunk_overlap=200)
    chunks=splitter.split_documents(documents)

    #3.向量化入库
    print("\n【步骤3】向量化入库...")
    retriever=KnowledgeRetriever()
    retriever.add_documents(chunks)

    #4.简单测试
    print("\n【测试检索】")
    test_query="transformer架构是什么?"
    print(f"查询：'{test_query}'")
    results=retriever.search(test_query,top_k=3)
    print(retriever.format_results(results))

if __name__ == "__main__":
    main()
