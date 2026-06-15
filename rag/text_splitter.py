"""
智能文本分块器
按 Markdown 标题、段落递归分块，保留语义完整性
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class SmartTextSplitter:
    """智能分块器，优先按 Markdown 标题边界切分"""
    def __init__(
            self,
            chunk_size:int=1000,
            chunk_overlap:int=200,
            separators:List[str]=None
    ):
        """
        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 相邻块之间的重叠字符数
            separators: 分隔符优先级列表
        """
        if separators is None:
            # Markdown 标题优先，逐级下降
            separators = [
                "\n# ",     # 一级标题
                "\n## ",    # 二级标题
                "\n### ",   # 三级标题
                "\n#### ",  # 四级标题
                "\n\n",     # 段落分隔
                "\n",       # 换行
                "。",       # 中文句号
                ". ",       # 英文句号
                " ",        # 空格（最后手段）
            ]
        
        self.splitter=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            keep_separator=True
        )

    def split_documents(self,documents:List[Document])->List[Document]:
        """
        对文档列表进行分块
        
        Args:
            documents: 原始文档列表
        
        Returns:
            分块后的文档列表，每个块保留原始元数据并附加块索引
        """
        all_chunks=[]

        for doc in documents:
            chunks=self.splitter.split_documents([doc])

            #为每个块添加块索引
            for i,chunk in enumerate(chunks):
                chunk.metadata["chunk_index"]=i
                chunk.metadata["chunk_total"]=len(chunks)
            
            all_chunks.extend(chunks)
        
        print(f"📦 分块完成：{len(documents)} 个文档 → {len(all_chunks)} 个块")
        return all_chunks