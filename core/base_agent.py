"""
Agent 基类
封装日志、异常处理、重试计数等通用逻辑
"""

import logging
from typing import Any
from state.agent_state import AgentState

# 配置日志
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

"""
为什么初始化要传 name？
核心作用：日志溯源。


self.name = name
self.logger = logging.getLogger(name)
这样每个日志都自动带上节点标识，输出像：


2026-06-13 10:00:01 - PlannerAgent - INFO - [PlannerAgent] 开始执行
2026-06-13 10:00:05 - RAGRetrieverAgent - INFO - [RAGRetrieverAgent] 开始执行
2026-06-13 10:00:08 - PlannerAgent - ERROR - [PlannerAgent] 执行错误: ConnectionError

"""

class BaseAgent:
    """所有 Agent 节点的基类"""
    def __init__(self,name:str):
        self.name=name
        self.logger=logging.getLogger(name)
    
    def log_start(self,state:AgentState)->None:
        """节点开始执行时记录日志"""
        self.logger.info(f"[{self.name}] 开始执行")

    def log_end(self,state:AgentState)->None:
        """节点执行结束时记录日志"""
        self.logger.info(f"[{self.name}] 执行完毕")

    def log_error(self,error:Exception,state:AgentState)->None:
        """节点执行时发生错误时记录日志"""
        self.logger.error(f"[{self.name}] 执行错误: {error}")

    def should_retry(self,state:AgentState)->bool:
        """判断节点是否需要重试"""
        return state.get("error_count",0) < state.get("max_retries",3)
    
    def increment_retry(self,state:AgentState)->AgentState:
        """增加重试计数"""
        state["error_count"]=state.get("error_count",0)+1
        return state
    
    def reset_retry(self,state:AgentState)->AgentState:
        """重置重试计数"""
        state["error_count"]=0
        return state
"""
为什么每个方法都要传 state: AgentState？
因为 state 是整个 LangGraph 流水线的"唯一数据通道"。

在这个项目中，Agent 以有向图（DAG）节点的形式串联，节点之间不共享内存、不直接互相调用。数据传递只有一条路：通过 state。

具体看你的方法：

should_retry(state) — 需要读 error_count 和 max_retries（来自 state）
increment_retry(state) — 需要往 state 里写 error_count，然后把更新后的 state 返回给框架
log_start/end(state) — 虽然当前没用到 state，但保持一致性，未来可能需要在日志里打印 state 里的信息（比如当前处理到第几步）
简单说：state 就是所有节点共享的"工单"，每个节点看完工单、填上自己的处理结果，交给下一个节点。

顺便提个建议
log_start/log_end/log_error 当前并没有实际使用 state 参数，纯粹是为了签名一致。如果短期内确实用不到，可以考虑去掉这个参数，避免每个子类继承后都要写个 state 参数却不用：


def log_start(self) -> None:
    self.logger.info(f"[{self.name}] 开始执行")
当然如果统一规范保留也无妨，只是多了个冗余参数。
"""