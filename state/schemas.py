"""
Pydantic 数据模型定义
用于 LLM 结构化输出和 API 交互
"""

from pydantic import BaseModel,Field
from typing import List,Optional

class IntentSchema(BaseModel):
    """意图理解的结构化输出"""
    objective:str=Field(...,description="用一句话自然语言概括用户想了解什么或实现什么（例如'了解Transformer架构的原理'，不要用分类标签）")
    constraints:List[str]=Field(default_factory=list,description="限制条件列表，如'需要中文回答'、'要具体步骤'等。无限制则为空列表")
    domain:str=Field(...,description="所属AI子领域，如NLP、CV、LLM应用、模型部署、推荐系统等。精确到具体子领域")
    complexity:str=Field(default="medium", description="复杂度：simple/medium/complex。纯知识问答为simple，涉及多步骤实现为complex")

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

# phase 4 增加的schemas字段
from datetime import datetime

class UserPreference(BaseModel):
    """用户偏好"""
    category:str=Field(...,description="用户偏好的类别")
    value:str=Field(...,description="用户偏好值")
    confidence:float=Field(default=0.8, ge=0, le=1, description="置信度")
    source:str=Field(default="inferred",description="来源:stated(用户明确)| inferred(推断)")

class KeyFact(BaseModel):
    """关键事实"""
    subject:str=Field(...,description="主题,如用户、项目A")
    predicate:str=Field(...,description="谓词，如 使用、偏好、部署于")
    object:str=Field(...,description="宾语，如 Python、AWS")
    timestamp:str=Field(default_factory=lambda:datetime.now().isoformat())
    confidence:float=1.0

class MemoryExtraction(BaseModel):
    """从对话中提炼的记忆条目"""
    preferences:List[UserPreference]=Field(default_factory=list)
    facts:List[KeyFact]=Field(default_factory=list)



