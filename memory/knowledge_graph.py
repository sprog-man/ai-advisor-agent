"""
温记忆-知识图谱（基于 networkx 内存版，可迁移至 Neo4j）
"""

import networkx as nx
from typing import List,Tuple,Optional

class WarmKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_triple(self,subject:str,predicate:str,obj:str,metadata:dict=None):
        """添加三元组
        等价于画一条从 subject 指向 obj 的有向边，边上标注 predicate（关系）和一些额外信息（metadata）。
        举例：
    graph.add_triple("张三", "使用", "Python", {"timestamp": "2026-06-16"})
    # 图中新增一条边：张三 --使用--> Python
        """
        self.graph.add_edge(subject,obj,predicate=predicate,**(metadata or {}))
    
    def query(self,subject:str=None,predicate:str=None,obj:str=None)->List[dict]:
        results=[]
        for s,o,data in self.graph.edges(data=True):
            if subject and s!=subject:
                continue
            if obj and o != obj:
                continue
            if predicate and data.get("predicate")!=predicate:
                continue
            results.append({
                "subject":s,
                "predicate":data["predicate"],
                "obj":o,
                **{k:v for k,v in data.items() if k!="predicate"}
            })
        """
        从图中查找匹配的三元组：


for s, o, data in self.graph.edges(data=True):
遍历图中每一条边，s 是起点，o 是终点，data 是边的属性（包含 predicate 和其他 metadata）。

然后用 subject、predicate、obj 三个参数做过滤，返回匹配的结果。

举例：


# 查所有"使用"的关系
graph.query(predicate="使用")
# 返回: [{"subject": "张三", "predicate": "使用", "obj": "Python", ...}]

# 查张三相关的所有关系
graph.query(subject="张三")
# 返回: [{"subject": "张三", "predicate": "使用", "obj": "Python", ...},
#        {"subject": "张三", "predicate": "偏好", "obj": "Python", ...}]

        """
        return results

    def get_related(self,node:str,depth:int=1)->list:
        """获取节点的邻域"""
        neighbors=list(nx.ego_graph(self.graph,node,radius=depth))
        return [{"subject":s,"predicate":d["predicate"],"object":t} for s,t,d in neighbors]
    
    """"
    ego_graph 是 networkx 的术语，"ego" 指的是"我自己"。
    ego_graph(graph, "张三", radius=1) 就是找出"张三"以及和他直接相连的所有点和边。

返回值是一个列表，每个元素是一个字典，包含 subject、predicate、object。

举例：


# 图中有：张三 --使用--> Python，Python --属于--> 编程语言
graph.get_related("张三", depth=1)
# 返回: [{"subject": "张三", "predicate": "使用", "object": "Python"},
#        {"subject": "Python", "predicate": "属于", "object": "编程语言"}]

    """
    