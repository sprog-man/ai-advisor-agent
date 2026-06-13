"""
统一配置中心
使用 Pydantic 自动校验环境变量，启动时如果缺少必要配置会直接报错
"""

import os
from pydantic import BaseModel,field_validator
from dotenv import load_dotenv
load_dotenv()

class LLMConfig(BaseModel):
    """LLM 模型配置"""
    api_key:str
    base_url:str
    model:str

    @field_validator("api_key")
    def api_key_must_not_be_empty(cls,v:str):
        if not v or v.startswith("your-api-key"):
            raise ValueError("LLM_API_KEY 未设置")
        return v
    
class EmbeddingConfig(BaseModel):
    """Embedding 模型配置"""
    api_key:str
    base_url:str
    model:str

class Settings(BaseModel):
    """全局配置"""
    llm:LLMConfig
    embedding:EmbeddingConfig

    # 项目路径
    """
    __file__ — 当前文件的路径（这里是 settings.py 的文件路径）
    os.path.abspath(__file__) — 把路径转为绝对路径（防止相对路径带来的问题）
    os.path.dirname(...) — 取上一层目录（即 config/ 文件夹）
    再套一层 os.path.dirname(...) — 再往上取一层，就是项目根目录（ai-advisor-agent/）
    """
    project_root:str=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    knowledge_base_dir:str=""
    chroma_db_dir:str=""

    def __init__(self,**data):
        """
        super().__init__(**data) — 调用父类的构造函数。这说明这个类继承自 pydantic.BaseModel（Pydantic 模型常用写法）
self.knowledge_base_dir = ... — 拼接出一个路径，赋值给 knowledge_base_dir 属性
这个 chroma_db_dir 的值会是 e:\MY-Study-Way\ai-advisor-agent\data\chroma_db
        """
        super().__init__(**data)
        self.knowledge_base_dir=os.path.join(self.project_root,"data","knowledge_base")
        self.chroma_db_dir=os.path.join(self.project_root,"data","chroma_db")

        #确保目录存在
        os.makedirs(self.knowledge_base_dir,exist_ok=True)
        os.makedirs(self.chroma_db_dir,exist_ok=True)

def load_settings() -> Settings:
    """从环境变量加载配置，缺失时抛出明确错误"""
    try:
        llm_config = LLMConfig(
            api_key=os.environ.get("LLM_API_KEY", ""),
            base_url=os.environ.get("LLM_BASE_URL", ""),
            model=os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
        )
    except Exception as e:
        print(f"[ERROR] LLM配置错误: {e}")
        print("请检查 .env 文件中的 LLM_API_KEY, LLM_BASE_URL, LLM_MODEL")
        raise

    embedding_config = EmbeddingConfig(
        api_key=os.environ.get("EMBEDDING_API_KEY", ""),
        base_url=os.environ.get("EMBEDDING_BASE_URL", ""),
        model=os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    )

    settings = Settings(llm=llm_config, embedding=embedding_config)

    print(f"[OK] 配置加载成功")
    print(f"   LLM: {settings.llm.base_url} -> {settings.llm.model}")
    
    return settings

# 全局单例，其他模块直接 import settings 即可
settings = load_settings()





