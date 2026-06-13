"""
LLM 工厂模块
提供统一的 LLM 实例创建接口，支持任意 OpenAI 兼容厂商
"""

from langchain_openai import ChatOpenAI
from config.settings import settings

def create_llm(temperature:float=0.0,max_tokens:int=4096)->ChatOpenAI:
    """
    创建 LLM 实例
    
    Args:
        temperature: 温度参数，0=确定性输出，适合拆解任务
        max_tokens: 最大输出token数
    
    Returns:
        ChatOpenAI 实例
    """
    return ChatOpenAI(
        api_key=settings.llm.api_key,
        base_url=settings.llm.base_url,
        model=settings.llm.model,
        temperature=temperature,
        max_tokens=max_tokens
    )

# 默认实例（确定性输出，用于任务拆解）
llm=create_llm(temperature=0.0)

# 创造性实例（用于生成总结等需要发挥的场景）
crateative_llm=create_llm(temperature=0.7)