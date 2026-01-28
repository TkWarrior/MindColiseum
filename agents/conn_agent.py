from states.states import DebateState
from llms.conn_agent_llm import conn_agent_llm

def conn_agent(state:DebateState):
    conn_argument = conn_agent_llm.generate_argument(
        topic=state["debate_topic"],
        pro_arguments=state["pro_arguments"],
        judge_comments=state["judge_comments"]
    )
    
    state["con_arguments"].append(conn_argument)
    state["transcript"].append({"speaker": "conn_agent", "argument": con_argument})
    state["current_agent"] = "pro_agent"
    
    return state