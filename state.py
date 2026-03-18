from typing import TypedDict, List, Optional

class StudioState(TypedDict):
    # 1. 用户的原始输入 (Agent A 接收)
    user_input: str
    input_images: Optional[List[str]]  # 图片的 URL 或本地路径
    input_links: Optional[List[str]]   # 网页链接
    
    # 2. 意图解析结果 (Agent A 输出)
    content_brief: str                 # 创作简报（主题、风格等）
    target_format: str                 # "图文" 或 "视频"
    
    # 3. 文案创作结果 (Agent B 输出)
    final_copywriting: str             # 最终用于小红书/飞书的文案
    visual_prompts: List[str]          # 拆解出来的，专门给生图/生视频 API 用的提示词
    
    # 4. 媒体生成结果 (Agent C 输出)
    generated_images: Optional[List[str]] # 生成的图片链接
    generated_videos: Optional[List[str]] # 生成的视频链接
    
    # 5. 审核与回溯机制 (Agent D 输出)
    is_approved: bool                  # 主编是否通过？
    revision_feedback: str             # 如果没通过，修改意见是什么？
    current_agent: str                 # 记录当前轮到哪个 Agent 干活

    # 【新增】6. 工程保护机制
    loop_count: int                    # 记录被打回重做的次数


    # 这是一个标准的 LangGraph 路由函数，它接收当前的 state，返回下一步要去的节点名称（字符串）
def route_after_editor(state: StudioState) -> str:
    """
    Agent D (主编) 执行完后，根据状态决定去向。
    返回 "END" 结束图，或者返回 "copywriter" 节点名称打回重做。
    """
    is_approved = state.get("is_approved", False)
    loop_count = state.get("loop_count", 0)
    
    # 面试亮点：防死循环机制
    MAX_RETRIES = 2 
    
    if is_approved:
        print("✅ 主编审核通过！准备将图文/视频推送到飞书。")
        return "approved"  # 这个字符串会映射到 LangGraph 的 END 节点
        
    elif loop_count >= MAX_RETRIES:
        # 如果已经重做了 2 次还是不合格，强制停止，避免 API 计费失控
        print(f"⚠️ 警告：已达到最大重做次数 ({MAX_RETRIES}次)。强制输出当前结果。")
        # 实际业务中，这里可以发一条飞书消息告诉用户：“这已经是尽力生成的版本了...”
        return "approved"  
        
    else:
        # 审核不通过，且还有重试机会，打回 Agent B 重新写文案和 Prompt
        print(f"❌ 审核不通过。打回重做。当前重试次数: {loop_count}。")
        print(f"主编反馈意见: {state.get('revision_feedback')}")
        return "rejected" # 这个字符串会映射回 "copywriter" 节点