"""
LLM 工厂模块
提供统一的 LLM 实例创建接口，支持任意 OpenAI 兼容厂商
"""

from langchain_openai import ChatOpenAI
from config.settings import settings

# 新增模块级缓存字典 _llm_cache = {}，以 (temperature, model) 为 key 缓存 ChatOpenAI
_llm_cache = {}
def create_llm(temperature:float=0.0,max_tokens:int=4096)->ChatOpenAI:
    """
    创建 LLM 实例
    
    Args:
        temperature: 温度参数，0=确定性输出，适合拆解任务
        max_tokens: 最大输出token数
    
    Returns:
        ChatOpenAI 实例
    """
    key=(temperature,settings.llm.model)
    if key not in _llm_cache:
        _llm_cache[key]=ChatOpenAI(
            api_key=settings.llm.api_key,
            base_url=settings.llm.base_url,
            model=settings.llm.model,
            temperature=temperature,
            max_tokens=max_tokens
    )
    return _llm_cache[key]


    
    

# 默认实例（确定性输出，用于任务拆解）
# llm=create_llm(temperature=0.0)
def call_llm(prompt:str)->str:
    """调用LLM 返回相应文本"""
    response=create_llm(temperature=0.0).invoke(prompt)
    return response.content


# 创造性实例（用于生成总结等需要发挥的场景）
def creative_llm(prompt: str) -> str:
    response = create_llm(temperature=0.7).invoke(prompt)
    return response.content