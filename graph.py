from langgraph.graph import StateGraph, END
# 假设我们之前定义的 StudioState 已经写在 state.py 里了
from state import StudioState 

# ==========================================
# 步骤 1：初始化状态图 (传入我们的"公文包"结构)
# ==========================================
workflow = StateGraph(StudioState)

# ==========================================
# 步骤 2：添加节点 (把 4 个员工拉进群)
# 这里假设 agent_a_analyst 等是具体的 Python 函数
# ==========================================
workflow.add_node("analyst", agent_a_analyst)       # Agent A: 解析输入
workflow.add_node("copywriter", agent_b_copywriter) # Agent B: 写文案与分镜
workflow.add_node("generator", agent_c_generator)   # Agent C: 调API生图/生视频
workflow.add_node("editor", agent_d_editor)         # Agent D: 主编审核质检

# ==========================================
# 步骤 3：设定工作流的起点
# 飞书消息一进来，第一个接单的永远是 Agent A
# ==========================================
workflow.set_entry_point("analyst")

# ==========================================
# 步骤 4：定义常规的流水线交接 (普通边)
# 也就是 A 干完给 B，B 干完给 C...
# ==========================================
workflow.add_edge("analyst", "copywriter")
workflow.add_edge("copywriter", "generator")
workflow.add_edge("generator", "editor")

# ==========================================
# 步骤 5：定义核心亮点 —— 质检与回溯循环 (条件边)
# ==========================================

# 这是一个路由判断函数，用来检查公文包里的状态
def check_approval(state: StudioState):
    if state.get("is_approved") == True:
        return "approved"  # 审核通过
    else:
        return "rejected"  # 审核不通过

# 给主编 (Agent D) 配置一条岔路口
workflow.add_conditional_edges(
    "editor",          # 从 editor 节点出发
    check_approval,    # 调用这个函数来判断该走哪条路
    {
        # 如果函数返回 "approved"，直接走到 LangGraph 的内置终点 (END)
        # 走到 END 后，系统就会把最终物料发给飞书用户
        "approved": END, 
        
        # 如果函数返回 "rejected"，这根线就会连回 "copywriter"
        # 带着修改意见 (revision_feedback) 重新写文案、重新生成
        "rejected": "copywriter" 
    }
)

# ==========================================
# 步骤 6：编译图，打包成可执行的 Agent 实例
# ==========================================
app = workflow.compile()
