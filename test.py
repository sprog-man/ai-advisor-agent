from config.settings import settings
from core.llm_factory import llm
from state.agent_state import AgentState, Task

print('✅ config.settings: 加载成功')
print('✅ core.llm_factory: LLM实例创建成功')
print('✅ state.agent_state: 数据结构定义成功')
print()
print(f'当前配置:')
print(f'  LLM Base URL: {settings.llm.base_url}')
print(f'  LLM Model: {settings.llm.model}')
print(f'  知识库目录: {settings.knowledge_base_dir}')