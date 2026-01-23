from states.states import DebateState
from llms.summary_agent_llm import summary_agent_llm

def summary_agent(state:DebateState):
    summary = summary_agent_llm.generate_summary(
        scores=state["scores"],
        transcript=state["transcript"]
    )
    
    state["transcript"].append({"speaker": "summary_agent", "argument": summary})   
    
    return state
