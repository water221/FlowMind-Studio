from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import StudioState

# 定义结构化输出格式
class CopywriterOutput(BaseModel):
    final_copywriting: str = Field(description="为社交媒体（如小红书/飞书）撰写的最终宣发文案，包含合适的Emoji和分段排版。若是视频格式则应偏向脚本口播。")
    visual_prompts: List[str] = Field(description="拆解出来的视觉提示词列表（Prompts），将直接喂给商业生图/生视频API。每个提示词描述一个独立画面/分镜的构图、主体、光影或动作。")

def agent_b_copywriter(state: StudioState) -> dict:
    """
    Agent B (Copywriter / 主笔) 的节点函数。
    接收Agent A提取的简报，输出最终文案和供生图/生视频API调用的提示词列表。
    如果有来自Editor节点的打回意见(revision_feedback)，会加入打回意见进行重写。
    """
    print("--- ✍️ Agent B (主笔) 启动：正在撰写文案与拆解视觉分镜 ---")
    
    # 1. 提取上游信息
    brief = state.get("content_brief", "无简报信息")
    target_format = state.get("target_format", "图文")
    feedback = state.get("revision_feedback", "")
    loop_count = state.get("loop_count", 0)
    
    # 获取刚在上一步捞出的 RAG 品牌约束字典
    brand_rule = state.get("brand_knowledge", "无特殊品牌约束。")
    
    # 2. 修改建议注入逻辑 (核心亮点：处理打回重做的逻辑)
    revision_context = ""
    if feedback and loop_count > 0:
        print(f"🔄 收到主编修改意见，正在进行第 {loop_count} 次重写...")
        revision_context = f"\n\n【重要要求！！！】\n这是第 {loop_count} 次修改该作品。主编/审核人员给出了以下反馈意见：\n『{feedback}』\n请务必吸取上述意见，对文案和画面提示词进行针对性重写！"

    # 3. 构造 Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """你是一位顶尖的宣发文案主笔兼分镜导演（Copywriter / 主笔）。
你的任务是根据上游的【创作简报】和【目标格式】，创作出以下内容：
1. 吸引人的最终宣发文案（final_copywriting）。
   - 如果目标格式是"图文"，文案应偏向社交媒体风格（如小红书），吸引眼球，带Emoji。
   - 如果目标格式是"视频"，文案应偏向短视频旁白配音/解说脚本。
2. 具体的视觉提示词列表（visual_prompts）。
   - 这是给下游的生图/生视频模型(MidJourney/Sora等)直接使用的纯英文或详细中文描述。
   - 请拆解成 2~4 个不同的画面。如果是图片，注意描述构图、色彩、镜头(如: 8k, photorealistic, cinematic lighting)。如果是视频，注意描述镜头运动和主体动作(如: camera panning, slow motion)。
   
【重要强制规范 (来自企业品牌知识库的检索结果 RAG)】
{brand_rule}
   {revision_context}
"""),
        ("user", """【创作简报】
{brief}

【目标生成格式】
{target_format}

请开始撰写文案并拆解视觉提示词。
""")
    ])
    
    import os
    # 4. 初始化 LLM，绑定结构化输出 (使用火山方舟 API)
    ark_model_id = os.environ.get("ARK_MODEL_ID", "请在此处填入你的火山模型接入点id(ep-...)")
    ark_api_key = os.environ.get("ARK_API_KEY", "")

    llm = ChatOpenAI(
        model=ark_model_id,
        api_key=ark_api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        temperature=0.7
    )
    structured_llm = llm.with_structured_output(CopywriterOutput)
    
    chain = prompt_template | structured_llm
    
    try:
        result = chain.invoke({
            "brief": brief,
            "target_format": target_format,
            "brand_rule": brand_rule,
            "revision_context": revision_context
        })
        
        final_copywriting = result.final_copywriting
        visual_prompts = result.visual_prompts
        
        # 兜底校验
        if not visual_prompts:
            visual_prompts = [f"Best quality, highly detailed scene corresponding to: {brief[:50]}"]
            
    except Exception as e:
        print(f"⚠️ Agent B 生成失败，使用默认值。错误: {e}")
        final_copywriting = f"基于简报：\n{brief}\n（由于网络或生成错误，这是备用默认文案）"
        visual_prompts = ["A default image or video scene, highly detailed, masterpieces, 4k"]

    print(f"✅ 主笔完工！共规划 {len(visual_prompts)} 个视觉分镜。")
    
    # 5. 更新状态字典
    return {
        "final_copywriting": final_copywriting,
        "visual_prompts": visual_prompts,
        "current_agent": "Agent B (Copywriter)"
    }
