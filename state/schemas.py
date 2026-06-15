"""
Pydantic 数据模型定义
用于 LLM 结构化输出和 API 交互
"""

from pydantic import BaseModel,Field
from typing import List,Optional

class IntentSchema(BaseModel):
    """意图理解的结构化输出"""
    objective:str=Field(...,description="一句话概括用户想实现什么或者想问什么")
    constraints:List[str]=Field(default_factory=list,description="限制条件列表")
    domain:str=Field(...,description="所属AI子领域，如NLP、CV、LLM应用等")
    complexity:str=Field(default="medium", description="复杂度：simple/medium/complex")

class TaskStep(BaseModel):
    """单个任务步骤"""
    id:int=Field(...,description="步骤序号")
    description:str=Field(...,description="任务描述")
    dependencies:List[int]=Field(default_factory=list,description="依赖步骤ID列表")
    detail:Optional[str]=Field(default=None,description="补充说明")

class PlanSchema(BaseModel):
    """任务拆解的整体输出"""
    steps:List[TaskStep]=Field(...,min_length=1,max_length=10,description="任务步骤列表")

class SearchQuery(BaseModel):
    """知识检索查询（未来工具调用时使用）"""
    query:str=Field(...,description="用于检索的查询字符串")
    top_k:int=Field(default=5,ge=1,le=20,description="返回结果数量")