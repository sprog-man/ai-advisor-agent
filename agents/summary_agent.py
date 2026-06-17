"""
总结输出 Agent
将任务计划转化为用户友好的自然语言总结
"""

import json
from core.base_agent import BaseAgent
from core.llm_factory import create_llm
from state.agent_state import AgentState

class SummaryAgent(BaseAgent):
    """负责生成面向用户的友好总结"""

    def __init__(self):
        super().__init__(name="SummaryAgent")
        self.llm=create_llm(temperature=0.7)

    def __call__(self,state:AgentState)->AgentState:

        self.log_start(state)

        try:
            # 格式化任务列表
            tasks_text=json.dumps(state["plan"],ensure_ascii=False,indent=2)

            prompt=f"""你是一个热情、专业的AI技术顾问。用户提出了一个想法，团队已经为ta拆解好了实现步骤。
现在请你用清晰、鼓励的语气向用户汇报。

用户意图：
{state["user_intent"]}

实现计划：
{tasks_text}

请按以下格式组织你的回复：

## 🎯 想法确认
用一句话肯定用户的想法，点出这个想法的价值或有趣之处。

## 📋 实现路径（共X步）
对每一步，用以下格式说明：
**第1步：[步骤标题]**
- 做什么：[简述]
- 为什么：[说明这一步的必要性]
- 依赖：[如果有依赖的前置步骤，说明"需要等第X步完成后才能开始"]

**第2步：...**
（依次列出所有步骤）

## 💡 建议与提醒
- 预估总体难度和所需时间
- 指出最关键的步骤
- 给出1-2条实用建议
- 鼓励用户动手开始

语气要求：专业但不生硬，像一位有经验的技术朋友在给出建议。"""
            response=self.llm.invoke(prompt)
            state["final_summary"]=response.content
            state["status"]="success"

            self.log_end(state)

        except Exception as e:
            self.log_error(e,state)
            # 出错时给一个简单总结
            steps=[f"{t['id']}. {t['description']}" for t in state["plan"]]
            state["final_summary"]=f"我帮你梳理了{len(steps)}个步骤：\n" + "\n".join(steps)
            state["status"]="success"
        debug_state = {k: v for k, v in state.items() if k != "messages"}
        print(f"[{self.name}] 输出预览:")
        print(json.dumps(debug_state, indent=2, ensure_ascii=False))

        return state

# 导出单例
summary_agent = SummaryAgent()