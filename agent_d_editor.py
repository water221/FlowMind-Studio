from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import StudioState

# 定义结构化输出格式
class EditorOutput(BaseModel):
    is_approved: bool = Field(description="审核是否全部通过？要求文案和画面描述完全契合简报。通过为True，不通过为False。")
    revision_feedback: str = Field(description="如果未通过，必须给出给主笔(Agent B)的严厉且具指导性的修改建议；如果已通过，输出'无需修改'。")

def agent_d_editor(state: StudioState) -> dict:
    """
    Agent D (Editor / 主编) 的节点函数。
    作为 LLM-as-a-Judge，评估生成的内容（文案与视觉提示词）是否符合原始创作简报的需求。
    如果发现偏题或质量不足，则打回重做并附带明确的修改意见。
    """
    print("--- 🧐 Agent D (主编) 启动：正在进行质量审核 (LLM-as-a-Judge) ---")
    
    # 1. 收集被审阅的上下文内容
    brief = state.get("content_brief", "")
    copywriting = state.get("final_copywriting", "")
    visual_prompts = state.get("visual_prompts", [])
    loop_count = state.get("loop_count", 0)
    
    # 将视觉分镜列表转化为字符串展示给 LLM
    visuals_text = "\n".join([f"分镜 {i+1}: {p}" for i, p in enumerate(visual_prompts)])
    
    # 2. 构造严格的审核 Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """你是一位极其严格的新媒体主编（Editor / 质检员）。
你的任务是对员工提交的【宣发文案】和【视觉分镜策划】进行最终审核，判断它们是否完美符合原始的【创作简报】要求。

审核标准：
1. 主题一致性：文案和分镜是否抓住了简报的核心主题？没有跑题？
2. 质量控制：如果是图文平台（如小红书），是否有网感？如果是视频，是否有镜头感？
3. 分镜合理性：画面提示词是否具有高度画面感且符合文案脉络？

如果满足以上所有条件，请判定为通过 (is_approved=True)。
如果有任何瑕疵（或完全偏题），请判定为不通过 (is_approved=False)，并给出具体的、手把手的修改意见 (revision_feedback)。
"""),
        ("user", """【创作简报 (需求)】
{brief}

【员工提交的文案】
{copywriting}

【员工提交的视觉分镜方案】
{visuals_text}

请进行审核并输出结果。
""")
    ])
    
    # 3. 初始化评价模型 (LLM-as-a-Judge 通常选用推理能力最强的模型，如 GPT-4o)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.1)  # temperature拉低，保证评判的稳定性和一致性
    structured_llm = llm.with_structured_output(EditorOutput)
    
    chain = prompt_template | structured_llm
    
    try:
        result = chain.invoke({
            "brief": brief,
            "copywriting": copywriting,
            "visuals_text": visuals_text
        })
        
        is_approved = result.is_approved
        feedback = result.revision_feedback
        
    except Exception as e:
        print(f"⚠️ Agent D 审核出错: {e}。默认放行。")
        is_approved = True
        feedback = ""
        
    print(f"✅ 审核结果: {'🟢 通过 (Approved)' if is_approved else '🔴 不通过 (Rejected)'}")
    if not is_approved:
        print(f"   📝 主编意见: {feedback}")
        
    # 4. 更新轮次逻辑（关键设计）
    # 如果没通过，且将走向下一轮重做，在这里预先递增 loop_count 计数器
    next_loop_count = loop_count
    if not is_approved:
        next_loop_count += 1
        
    return {
        "is_approved": is_approved,
        "revision_feedback": feedback,
        "current_agent": "Agent D (Editor)",
        "loop_count": next_loop_count
    }
