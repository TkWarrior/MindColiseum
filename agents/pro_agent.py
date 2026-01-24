from states.states import DebateState
from llms.pro_agent_llm import pro_agent_llm

def pro_agent(state:DebateState):
    state["debate_topic"] = "Will AI replace human jobs in the next 20 years?"
    pro_arguement = pro_agent_llm.generate_argument(
        topic=state["debate_topic"],
        conn_arguments=state["con_arguments"],
        judge_comments=state["judge_comments"]
    )
    
    print("pro arguements : " + state["pro_arguments"].append(pro_arguement))
    state["transcript"].append({"speaker": "pro_agent", "argument": pro_arguement})
    state["current_agent"] = "conn_agent"
    
    return state