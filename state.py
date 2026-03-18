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
