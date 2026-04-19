import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# 引用我们之前封装好的图实例
from graph import app

load_dotenv()

server = FastAPI(
    title="FlowMind Studio API",
    description="企业级多智能体自动化媒体宣发微服务引擎",
    version="1.0"
)

# 前端发来请求的数据结构
class StudioRequest(BaseModel):
    user_input: str
    thread_id: str = "demo_thread_001"  # 允许前端传过来 Thread ID，区分不同用户会话

@server.post("/api/workflow/start")
async def start_workflow(req: StudioRequest):
    """
    第一阶段接口：启动工作流生成文案，并在遇到'生图拦截点(HITL)'时挂起并推送消息给前端。
    采用 Server-Sent Events (SSE) 协议推流，避免客户端等待导致超时（Timeout）。
    """
    def event_generator():
        initial_state = {
            "user_input": req.user_input,
            "input_images": [],
            "input_links": [],
            "loop_count": 0
        }
        config = {
            "configurable": {"thread_id": req.thread_id},
            "recursion_limit": 10
        }
        
        try:
            yield f"data: {json.dumps({'status': 'START', 'msg': '🔥 FlowMind流水线启动...'})}\n\n"
            
            # 使用同步的 Generator yield 实时日志，这在流式 API（如飞书推送）中很常见
            for step_result in app.stream(initial_state, config):
                for agent_name, state_update in step_result.items():
                    # 我们过滤一下输出给前端的信息，减少无用数据
                    info = {
                        "agent": agent_name,
                        "current_brief": state_update.get("content_brief", ""),
                        "final_copywriting": state_update.get("final_copywriting", ""),
                        "visual_prompts_count": len(state_update.get("visual_prompts", []))
                    }
                    yield f"data: {json.dumps(info, ensure_ascii=False)}\n\n"
            
            # 运行停止后，获取一下这根 Thread 的当前状态
            state_status = app.get_state(config)
            
            # 判断是不是触发了我们的“生图人工断点”
            if state_status.next and "generator" in state_status.next:
                hitl_msg = {
                    "status": "HITL_PAUSE",
                    "msg": "🛑 流程已挂起：文案与分镜生成完毕。请调用 /api/workflow/approve 接口授权资金放行以生图。"
                }
                yield f"data: {json.dumps(hitl_msg, ensure_ascii=False)}\n\n"
            else:
                yield f"data: {json.dumps({'status': 'DONE', 'msg': '全流程结束'})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'status': 'ERROR', 'msg': str(e)})}\n\n"

    # 使用 StreamingResponse 让接口变成打字机一样的“推流”模式
    return StreamingResponse(event_generator(), media_type="text/event-stream")


class ApproveRequest(BaseModel):
    thread_id: str = "demo_thread_001"

@server.post("/api/workflow/approve")
async def approve_workflow(req: ApproveRequest):
    """
    第二阶段接口：管理员点击“同意”后回调该接口，将这根 Thread (进程) 唤醒，继续生图和审核。
    """
    def event_generator():
        config = {"configurable": {"thread_id": req.thread_id}, "recursion_limit": 10}
        state_status = app.get_state(config)
        
        if not state_status.next or "generator" not in state_status.next:
            yield f"data: {json.dumps({'error': '当前没有等待您审批的生成任务或已被处理！'})}\n\n"
            return
            
        try:
            yield f"data: {json.dumps({'status': 'RESUME', 'msg': '✅ 授权成功，正在恢复生图服务...'})}\n\n"
            
            # 入参置 None 让它从 Checkpointer 里拿上次的记忆直接往下跑
            for step_result in app.stream(None, config):
                for agent_name, state_update in step_result.items():
                    info = {
                        "agent": agent_name,
                        "generated_images": state_update.get("generated_images", []),
                        "is_approved": state_update.get("is_approved", True),
                        "revision_feedback": state_update.get("revision_feedback", "")
                    }
                    yield f"data: {json.dumps(info, ensure_ascii=False)}\n\n"
                    
            yield f"data: {json.dumps({'status': 'DONE', 'msg': '🎉 宣发物料产出完毕！'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'ERROR', 'msg': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    print("🚀 FlowMind Studio Server 启动中...")
    print("👉 接口文档地址：http://127.0.0.0:8000/docs")
    # 为了方便你跑演示，这里内嵌使用了 uvicorn 启动
    uvicorn.run("server:server", host="0.0.0.0", port=8000, reload=True)
