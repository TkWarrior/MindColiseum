from states.states import DebateState
from llms import conn_agent_llm

def conn_agent(state:DebateState):
    conn_argument = conn_agent_llm.generate_argument(
        topic=state["debate_topic"],
        pro_arguments=state["pro_arguments"],
        judge_comments=state["judge_comments"]
    )
    
    state["conn_arguments"].append(conn_argument)
    print("conn arguments : ",state["conn_arguments"])
    # state["transcript"].append({"speaker": "conn_agent", "argument": conn_argument})
    state["current_agent"] = "pro_agent"
    
    return {
        "conn_arguments":state["conn_arguments"],
        "transcript": [
            {
                "role": "assistant",
                "content": f"[CON] {conn_argument}"
            }
        ],
        "current_agent":state["current_agent"]
    }