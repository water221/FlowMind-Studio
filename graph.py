from langgraph.graph import StateGraph, END
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

app = workflow.compile()

