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
    # configurable 中的 thread_id 用于区分不同用户的聊天会话，实现各自状态的隔离恢复
    config = {
        "configurable": {"thread_id": "demo_thread_001"},
        "recursion_limit": 10
    }
    
    try:
        # 维护一个完整的状态字典
        current_state = initial_state.copy()
        
        # --- 第一次执行阶段：运行到人工审核拦截点之前 ---
        for step_result in app.stream(initial_state, config):
            for agent_name, state_update in step_result.items():
                print(f"\n📦 当前处理节点: [{agent_name}]")
                current_state.update(state_update)
                
                if "final_copywriting" in state_update:
                    print(f"📝 截获文案片段:\n{state_update['final_copywriting']}")
                    
        # --- 查看当前图流转状态，触发风控卡点（HITL） ---
        state_status = app.get_state(config)
        next_node = state_status.next
        
        if "generator" in next_node:
            print("\n" + "="*50)
            print("🚨 【触发风控断点 / HITL】🚨")
            print("➡️ Agent B 已完成文案和分镜设计。接下来将调用[高成本生图API]。")
            print("请主编(即正在运行测试的您)评估前置文案和分镜质量：")
            print(f"当前准备使用的提示词数：{len(current_state.get('visual_prompts', []))}个")
            print("="*50)
            
            user_decision = input("\n请问是否授权放行(Y/N)？ (输入 'y' 继续生成，输入 'n' 驳回整条流程): ")
            
            if user_decision.strip().lower() == 'y':
                print("\n✅ 人工审批通过，授权继续...")
                # 重新恢复图的运行，入参为 None 表示接着原来的断点状态继续往下跑
                for step_result in app.stream(None, config):
                    for agent_name, state_update in step_result.items():
                        print(f"\n📦 当前处理节点(续): [{agent_name}]")
                        current_state.update(state_update)
            else:
                print("\n❌ 审批不通过，工作流已终止。")
                # 不再执行 generator，直接结束并返回
                return
                
        # 记录最后拼装完成的全部状态
        final_state = current_state
                
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
