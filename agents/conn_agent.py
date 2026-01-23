from states.states import DebateState

def conn_agent(state:DebateState):
    con_argument = conn_agent_llm.generate_argument(
        topic=state["debate_topic"],
        pro_arguments=state["pro_arguments"],
        judge_comments=state["judge_comments"]
    )
    
    state["con_arguments"].append(con_argument)
    state["transcript"].append({"speaker": "conn_agent", "argument": con_argument})
    state["current_agent"] = "pro_agent"
    
    return state