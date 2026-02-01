from states.states import DebateState
from llms import summary_agent_llm

def summary_agent(state:DebateState):
    summary = summary_agent_llm.generate_summary(
        scores=state["scores"],
        transcript=state["transcript"]
    )
    print("SUMMARY:", summary)
    # state["transcript"].append({"speaker": "summary_agent", "argument": summary})   
    
    return {
        "transcript": [
                {
                    "role": "assistant",
                    "content": f"[SUMM] {summary}"
                }
                ],
        "summary":summary
    }
