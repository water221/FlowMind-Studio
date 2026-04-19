from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from state import StudioState
from knowledge_base import retrieve_knowledge

# 定义期待的结构化输出格式
class AnalystOutput(BaseModel):
    content_brief: str = Field(description="提取的创作简报，包含核心主题、风格、受众及关键信息定调")
    target_format: str = Field(description="目标生成格式，必须严格是 '图文' 或 '视频' 两个词之一")

def agent_a_analyst(state: StudioState) -> dict:
    """
    Agent A (Analyst / 感知器) 的节点函数。
    接收用户的多模态输入，输出创作简报与目标格式，并更新全局状态。
    """
    print("--- 🤖 Agent A (感知器) 启动：正在解析用户输入 ---")
    
    # 1. 提取当前状态中的输入内容
    user_input = state.get("user_input", "")
    input_images = state.get("input_images", [])
    input_links = state.get("input_links", [])
    
    # 🌟 [RAG 亮点]: 在理解意图时，顺手去企业词向量知识库里把最接近该意图的“标杆/指导原则”捞出来
    brand_rule = retrieve_knowledge(user_input, n_results=2)
    print(f"📖 触发 RAG 检索！命中品牌规则：\n   {brand_rule}")

    # 2. 构造 Prompt，指导大模型进行意图识别
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", """你是一个资深的宣发媒体策划（Analyst / 感知器）。
你的任务是解析用户的输入（可能包含文本、图片URL、网页链接）。
你需要：
1. 提炼出一份清晰的【创作简报 (content_brief)】，概述核心主题、情感基调、受众目标等。
2. 识别出用户想要生成的【目标形式 (target_format)】，只能从 "图文" 或 "视频" 中二选一。如果没有明确提及，请根据内容特征进行合理推测（如：包含动作/过程倾向选视频，静态展示倾向选图文）。
"""),
        ("user", """【用户原始输入】
文本: {user_input}
关联图片/URL: {input_images}
关联链接: {input_links}

请提取简报及目标形式。
""")
    ])
    
    import os
    # 3. 初始化 LLM 并绑定结构化输出 (接入火山方舟 API)
    # 通过环境变量读取火山的接入点 ID（ep-xxx）
    ark_model_id = os.environ.get("ARK_MODEL_ID", "请在此处填入你的火山模型接入点id(ep-...)")
    ark_api_key = os.environ.get("ARK_API_KEY", "")
    
    llm = ChatOpenAI(
        model=ark_model_id,
        api_key=ark_api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        temperature=0.7
    )
    structured_llm = llm.with_structured_output(AnalystOutput)
    
    # 4. 组装 Chain 并调用
    chain = prompt_template | structured_llm
    
    try:
        result = chain.invoke({
            "user_input": user_input,
            "input_images": input_images if input_images else "无",
            "input_links": input_links if input_links else "无"
        })
        
        brief = result.content_brief
        format_type = result.target_format
        
        # 兜底校验格式
        if format_type not in ["图文", "视频"]:
            format_type = "图文"
            
    except Exception as e:
        print(f"⚠️ Agent A 解析失败，使用默认值。错误: {e}")
        brief = f"基于以下内容生成的媒体物料: {user_input}"
        format_type = "图文"
        
    print(f"✅ 解析完成！目标格式: {format_type} | 简报摘要: {brief[:30]}...")
    
    # 5. 返回要更新的状态字典
    # 返回了 RAG 捞到的品牌原则 brand_knowledge ，以便下个节点使用
    return {
        "content_brief": brief,
        "target_format": format_type,
        "brand_knowledge": brand_rule,
        "current_agent": "Agent A (Analyst)",
        "loop_count": state.get("loop_count", 0)
    }
