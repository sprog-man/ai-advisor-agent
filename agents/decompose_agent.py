"""
任务拆解 Agent
将结构化的用户意图，"Phase2新增：结合知识库检索结果"，拆解为具体可执行的任务步骤
"""

import json
from core.base_agent import BaseAgent
from core.llm_factory import create_llm
from state.agent_state import AgentState, Task
from state.schemas import PlanSchema

class DecomposeAgent(BaseAgent):
    """负责将意图拆解为有序任务列表"""

    def __init__(self):
        super().__init__(name="DecomposeAgent")
        self.structured_llm = create_llm(temperature=0.5).with_structured_output(PlanSchema)

    def __call__(self,state:AgentState)->AgentState:
        self.log_start(state)
        self.reset_retry(state)

        try:
            #构建Prompt，注入上下文
            knowledge_context=state.get("knowledge_context","")
            knowledge_section=""
            if knowledge_context and knowledge_context != "未找到相关知识。":
                knowledge_section = f"""
## 参考资料（来自你的私有知识库）
{knowledge_context}

## 说明
请参考上述资料中的最佳实践和技术方案来拆解任务。
如果资料中有相关代码示例或架构设计，请融入步骤中。
"""

            prompt=f"""你是一个资深技术项目经理，擅长将模糊的技术想法拆解为可执行的步骤。

用户意图：
{state["user_intent"]}
{knowledge_section}

请将上述意图拆解为具体实现步骤。返回JSON数组（严格格式，不要包含```json```标记）：

[
    {{
        "id": 1,
        "description": "具体可执行的任务描述",
        "dependencies": [],
        "detail": "这一步的补充说明，为什么要做这一步，涉及什么技术"
    }},
    {{
        "id": 2,
        "description": "第二个任务",
        "dependencies": [1],
        "detail": "说明"
    }}
]

拆解原则：
1. 第一步的dependencies为空数组[]
2. 后续步骤明确标注依赖哪些前面步骤的id
3. 每个步骤必须是可独立完成的小任务，不要出现"完成整个系统"这种模糊描述
4. 步骤数量控制在4-7个
5. 步骤要具体，比如"使用FastAPI创建/api/chat接口"而不是"写接口"
6. 按照逻辑依赖关系排序，先基础后上层
7. 如果参考资料中有相关方案，优先采用资料中的建议"""
            
            # 最初非schemas规定化输出使用LangChain的structured_llm，
            # response=call_llm(prompt)

            # # 解析JSON
            # try:
            #     tasks_data=json.loads(response)
            # except json.JSONDecodeError:
            #     content=response.strip()
            #     start=content.find('[')
            #     end=content.rfind(']')+1
            #     tasks_data=json.loads(content[start:end])
            
            # # 转换为字典列表（LangGraph的TypedDict要求序列化类型）
            # state["plan"]=[
            #     {
            #         "id":t["id"],
            #         "description":t["description"],
            #         "dependencies":t.get("dependencies",[]),
            #         "status":"pending",
            #         "result":None
            #     }
            #     for t in tasks_data
            # ]

            # self.logger.info(f"拆解出 {len(state['plan'])} 个任务步骤")
            # self.log_end(state)
            # 使用schemas 规定化输出
            plan:PlanSchema = self.structured_llm.invoke(prompt)
            # 转换为状态存储的格式
            state["plan"]=[
                {
                    "id":step.id,
                    "description":step.description,
                    "dependencies":step.dependencies,
                    "status":"pending",
                    "result":None
                }
                for step in plan.steps
            ]
            self.logger.info(f"成功拆解出 {len(state['plan'])} 个步骤")
            self.log_end(state)

        except Exception as e:
            self.log_error(e,state)
            # 出错时创建兜底计划
            state["plan"]=[
                {
                    "id": 1,
                    "description": "分析用户需求，明确技术方案",
                    "dependencies": [],
                    "status": "pending",
                    "result": None
                },
                {
                    "id": 2,
                    "description": "根据分析结果逐步实现",
                    "dependencies": [1],
                    "status": "pending",
                    "result": None
                }
            ]
        debug_state = {k: v for k, v in state.items() if k != "messages"}
        print(f"[{self.name}] 输出预览:")
        print(json.dumps(debug_state, indent=2, ensure_ascii=False))

        
        return state
    
# 导出单例
decompose_agent = DecomposeAgent()
            
