"""
冷记忆-原始对话日志（SQLite）
"""

import sqlite3
import os
import json
from datetime import datetime

class ColdLogStore:
    def __init__(self, db_path: str = None):

        """
        默认数据库路径是 memory/../data/cold_logs.db
        （即项目根目录的 data/cold_logs.db）
连接 SQLite 数据库
注意：第 15 行写的是 self.__init__table()（两个下划线开头），但第 17 行方法名是 _init_table（一个下划线）。
        """
        if db_path is None:
            db_path=os.path.join(os.path.dirname(__file__),"..","data","cold_logs.db")
        self.conn =sqlite3.connect(db_path)
        self._init_table()

    def _init_table(self):
        # 创建 logs 表：
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            timestamp TEXT,
            role TEXT,
            content TEXT,
            metadata TEXT
        )
        """)
        self.conn.commit()
    
    def log(self,thread_id:str,role:str,content:str,metadata:dict=None):
        self.conn.execute(
            "INSERT INTO logs (thread_id, timestamp, role, content, metadata) VALUES (?,?,?,?,?)",
            (thread_id,datetime.now().isoformat(),role,content,json.dumps(metadata or {}))
        )
        self.conn.commit()
        # 每次 Agent 处理一轮对话时，把每条消息都记下来。

    def get_history(self,thread_id:str,limit:int=100)->list:
        # 从数据库中取出某个会话最近的 N 条消息
        # 按 id 降序排列（最新的在前），最多返回 limit 条。
        cursor=self.conn.execute(
            "SELECT role, content, timestamp FROM logs WHERE thread_id=? ORDER BY id DESC LIMIT ?",
            (thread_id,limit)
        )
        return [{"role": row[0], "content": row[1], "timestamp": row[2]} for row in cursor.fetchall()]
        