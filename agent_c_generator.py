import time
from typing import List
from state import StudioState

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
            # 真实对接示例（注释保留展示工程能力）：
            # from openai import OpenAI
            # client = OpenAI()
            # response = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
            # image_url = response.data[0].url
            
            # 使用模拟的延迟和返回值以保证无阻碍运行本地测试
            time.sleep(1.5)  # 模拟 API 网络请求耗时
            fake_image_url = f"https://mock-media-ai.com/generated_image_scene_{i+1}_{int(time.time())}.png"
            generated_images.append(fake_image_url)
            print(f"  🖼️ 图片生成成功: {fake_image_url}")
            
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
