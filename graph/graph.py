from langgraph.graph import StateGraph
from states.states import DebateState
from agents.pro_agent import pro_agent
from agents.conn_agent import conn_agent
from agents.judge_agent import judge_agent
from agents.summary_agent import summary_agent

graph = StateGraph(DebateState)

graph.set_entry_point("pro_agent")  ## Starting point of the graph
graph.add_node("pro_agent", pro_agent)
graph.add_node("conn_agent", conn_agent)    
graph.add_node("judge_agent", judge_agent)
graph.add_node("summary_agent", summary_agent)
graph.set_finish_point("summary_agent")  ## Ending point of the graph

graph.add_edge("pro_agent", "conn_agent")
graph.add_edge("conn_agent", "judge_agent")
graph.add_edge("judge_agent", "summary_agent")

graph.add_conditional_edges(
    "judge_agent",
    lambda state: "summary_agent" if state["debate_over"] else "pro_agent",
    {"pro_agent": "pro_agent", "summary_agent": "summary_agent"}
)

agent = graph.compile()
