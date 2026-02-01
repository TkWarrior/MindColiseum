from states.states import DebateState
from llms import pro_agent_llm

def pro_agent(state:DebateState):
    print("debate topic",state["debate_topic"])
    pro_argument = pro_agent_llm.generate_argument(
        topic=state["debate_topic"],
        conn_arguments=state["conn_arguments"],
        judge_comments=state["judge_comments"] 
    )
    state["pro_arguments"].append(pro_argument)
    print("pro arguments : ",state["pro_arguments"])
    # state["transcript"].append(pro_argument)
    state["current_agent"] = "conn_agent"
    
    return {"pro_arguments":state["pro_arguments"],
             "transcript": [
                {
                    "role": "assistant",
                    "content": f"[PRO] {pro_argument}"
                }
                ],
            "current_agent":state["current_agent"]}