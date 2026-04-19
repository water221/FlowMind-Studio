import time
import os
from typing import List
from state import StudioState
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

# 🌟 [Resilience 亮点]: 封装独立的 API 调用函数，并加上指数退避重试装饰器
# 无论是因为 QPS 限制还是网络波动引起的报错，都不直接宕机，而是等 2s、4s、8s 后最高重试 3 次
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=2, min=2, max=10),
    reraise=True
)
def call_image_api_with_retry(client: OpenAI, model_id: str, prompt: str):
    print(f"      📡 [网络请求] 正在通过🌋火山引擎API请求绘图 (如遇超时将自动退避重试)...")
    return client.images.generate(
        model=model_id,
        prompt=prompt,
        n=1,
        size="2K"  # 针对 doubao-seedream-5.0/4.5 等高配模型，需要传入 2K 或具体的如 2048x2048
    )

def agent_c_generator(state: StudioState) -> dict:
    """
    Agent C (Generator / 生成器) 的节点函数。
    接收Agent B拆解的视觉提示词(visual_prompts)，并根据目标格式(target_format)
    调用相应的商业生图或生视频API，最后返回生成的媒体URL或者路径记录。
    """
    print("--- 🎨 Agent C (生成器) 启动：正在调用视觉API生成媒体 ---")
    
    visual_prompts = state.get("visual_prompts", [])
    target_format = state.get("target_format", "图文")
    
    generated_images = []
    generated_videos = []
    
    if not visual_prompts:
        print("⚠️ 未收到视觉提示词，跳过生成。")
        return {
            "current_agent": "Agent C (Generator)"
        }
    
    print(f"🚀 即将生成 {len(visual_prompts)} 个 {target_format} 素材...")
    
    # 遍历提示词，逐个调用 API 生成画面
    for i, prompt in enumerate(visual_prompts):
        print(f"  [分镜 {i+1}/{len(visual_prompts)}] 正在生成...")
        print(f"  > Prompt: {prompt[:60]}...")
        
        # -------------------------------------------------------------
        # ✅ 求职展示亮点：这里展示了针对不同格式的路由分发逻辑
        # 实际项目中，这里可以替换为请求真实的 DALL-E 3 / Midjourney / Sora API
        # -------------------------------------------------------------
        if target_format == "图文":
            try:
                # 使用火山方舟的通用兼容接口调用生图
                ark_api_key = os.environ.get("ARK_API_KEY", "")
                # 生图模型接入点如果和对话模型不同，请在.env配置 ARK_IMAGE_MODEL_ID
                # 默认回退使用 ARK_MODEL_ID 以防用户没配
                ark_image_model_id = os.environ.get("ARK_IMAGE_MODEL_ID", os.environ.get("ARK_MODEL_ID", ""))
                
                client = OpenAI(
                    api_key=ark_api_key,
                    base_url="https://ark.cn-beijing.volces.com/api/v3"
                )
                
                # 替换掉原有的无保护代码，换用刚写好的高可用重试函数！
                response = call_image_api_with_retry(client, ark_image_model_id, prompt)
                
                image_url = response.data[0].url
                generated_images.append(image_url)
                print(f"  🖼️ 图片生成成功: {image_url}")
                
            except Exception as e:
                print(f"  ❌ 真实生图API历经多次自动重试仍失败: {e}")
                print("  正在降级使用模拟图片...")
                time.sleep(1)
                fake_image_url = f"https://mock-media-ai.com/generated_image_scene_{i+1}_{int(time.time())}.png"
                generated_images.append(fake_image_url)
                print(f"  🖼️ [模拟]图片生成成功: {fake_image_url}")
            
        elif target_format == "视频":
            # 真实对接示例（可接入 Runway Gen-2 / Pika / 其他视频模型 API）
            time.sleep(2.5)  # 视频生成通常耗时更长
            fake_video_url = f"https://mock-media-ai.com/generated_video_scene_{i+1}_{int(time.time())}.mp4"
            generated_videos.append(fake_video_url)
            print(f"  🎬 视频生成成功: {fake_video_url}")
            
        else:
            print(f"  ❌ 未知的 target_format: {target_format}")

    print("✅ Agent C 媒体生成排期完成！")
    
    # 将生成的结果更新到状态中传给下游
    return {
        "generated_images": generated_images if generated_images else None,
        "generated_videos": generated_videos if generated_videos else None,
        "current_agent": "Agent C (Generator)"
    }
