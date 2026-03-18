import json
import os
from dotenv import load_dotenv
from graph import app

# 加载可能存在的 .env 文件 (用于读取 OPENAI_API_KEY 等)
load_dotenv()

def print_separator(title=""):
    print(f"\n{'='*20} {title} {'='*20}")

def run_project_demo():
    print_separator("FlowMind Studio - 自动化媒体创作集群启动")
    
    # 提示确保有环境变量
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️ 警告: 未检测到 OPENAI_API_KEY 环境变量，程序可能会由于 LLM 鉴权失败而走默认异常分支。")
    
    # 构建测试用的初始状态，这相当于用户在飞书里发给机器人的一段话
    initial_state = {
        "user_input": "帮我写一篇关于我们公司新上线的 AI 编程助手的宣传文案，主要面向求职者展示自动写代码的功能，配几张有科技感的插图。要有网感。",
        "input_images": [],
        "input_links": [],
        "loop_count": 0  # 初始轮次设为0
    }
    
    print(f"👤 【用户原始输入】: {initial_state['user_input']}")
    print_separator("开始流水线作业")
    
    # app.stream 允许我们看到每一个 Agent (节点) 的流式输出结果
    # config 中可以配置 recurse_limit (防止图无限死循环跑爆)
    config = {"recursion_limit": 10}
    
    try:
        final_state = None
        for step_result in app.stream(initial_state, config):
            for agent_name, state_update in step_result.items():
                print(f"\n📦 当前处理节点: [{agent_name}]")
                # 这里可以对阶段性的局部状态做简单的打印展示
                if "final_copywriting" in state_update:
                    print(f"📝 截获文案:\n{state_update['final_copywriting']}")
                
                # 记录最后一步更新的状态来做最终拼装
                final_state = state_update
                
    except Exception as e:
        print(f"\n❌ 图执行过程中发生错误: {e}")
        return

    print_separator("全流程执行完毕，最终交付物料")
    
    if final_state:
        print("\n【最终文案内容】:")
        print(final_state.get("final_copywriting", "无"))
        
        print("\n【视觉资产生成链接】:")
        if final_state.get("generated_images"):
            for idx, img in enumerate(final_state.get("generated_images")):
                print(f" - 图片 {idx+1}: {img}")
        elif final_state.get("generated_videos"):
            for idx, vid in enumerate(final_state.get("generated_videos")):
                print(f" - 视频 {idx+1}: {vid}")
        else:
            print(" - 未产出任何多模态资产。")
    
    print("\n🎉 测试流程结束。如果在面试展示中，请着重展示中间被打回循环（如果有的话）的那一段日志，这是该架构的亮点。")

if __name__ == "__main__":
    run_project_demo()
