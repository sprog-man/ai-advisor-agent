"""
命令行交互入口
启动后可以与Agent进行对话交互
"""

from config.settings import settings
from graph.main_graph import app

def print_banner():
    print("=" * 60)
    print("  🤖 AI Advisor Agent — 你的专属AI技术顾问")
    print("=" * 60)
    print(f"  模型：{settings.llm.model}")
    print(f"  服务：{settings.llm.base_url}")
    print()
    print("  输入你的想法或问题，我会帮你拆解成具体步骤。")
    print("  输入 'quit' 或 'exit' 退出。")
    print("=" * 60)
    print()

def main():
    print_banner()

    while True:
        try:
            user_input=input("\n 你:").strip()

        except (EOFError,KeyboardInterrupt):
            print("\n\n👋 再见！")
            break

        if not user_input: continue

        if user_input.lower() in ["quit", "exit","q"]:
            print("👋 再见！")
            break

        #准备初始状态
        initial_state={
            "messages":[{"role":"user","content":user_input}],
            "user_intent":"",
            "plan":[],
            "knowledege_context":"",
            "final_summary":"",
            "error_count":0,
            "max_retries":3,
            "current_checkpoint_id":None,
            "status":"running"
        }

        print("\n⏳ 正在分析你的想法...")

        try:
            result=app.invoke(initial_state)
            print(f"\n{result['final_summary']}\n")
            print("-" * 60)
        except Exception as e:
            print(f"\n❌ 出错了：{e}")
            print("请重试，或者换一种方式描述你的想法。")

if __name__ == "__main__":
    main()