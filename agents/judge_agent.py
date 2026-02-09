from states.states import DebateState
from llms import judge_agent_llm

def judge_agent(state:DebateState):
       
    comments, updated_score = judge_agent_llm.evaluate_arguments(
        pro_arguments=state["pro_arguments"],
        conn_arguments=state["conn_arguments"],
    )
    
    print("JUDGE COMMENTS:", comments)
    state["judge_comments"].append(comments)
    print("SCORES BEFORE:", state["scores"])

    # Track per-round scores
    state["round_scores"].append(updated_score)

    for side , score in updated_score.items():
        state["scores"][side] += score
    
    state["round_no"] += 1
    
    print("SCORES AFTER:", state["scores"])

    if state["round_no"] > state["max_rounds"]:
        state["debate_over"] = True
    
    return {
        "judge_comments":state["judge_comments"],
        "scores":state["scores"],
        "round_scores":state["round_scores"],
        "round_no":state["round_no"],
        "debate_over":state["debate_over"]
    }