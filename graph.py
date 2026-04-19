from langgraph.graph import StateGraph, END
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from state import StudioState, route_after_editor
from agent_a_analyst import agent_a_analyst
from agent_b_copywriter import agent_b_copywriter
from agent_c_generator import agent_c_generator
from agent_d_editor import agent_d_editor

workflow = StateGraph(StudioState)

workflow.add_node("analyst", agent_a_analyst)
workflow.add_node("copywriter", agent_b_copywriter)
workflow.add_node("generator", agent_c_generator)
workflow.add_node("editor", agent_d_editor)

workflow.set_entry_point("analyst")

workflow.add_edge("analyst", "copywriter")
workflow.add_edge("copywriter", "generator")
workflow.add_edge("generator", "editor")

workflow.add_conditional_edges(
    "editor",
    route_after_editor,
    {
        "approved": END,
        "rejected": "copywriter"
    }
)

# 配置 SqliteSaver 持久化，存放在本地 checkpoints.sqlite 文件中
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

# 编译图时，加入持久化记忆配置，并设定风控断点 (在执行 generator 前强行停止)
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["generator"]
)

