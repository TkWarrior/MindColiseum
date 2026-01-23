
def judge_agent(state:DebateState):
    
    comments, updated_score = jusdge_agent_llm.evaluate_arguements(
        pro_arguements=state["pro_arguments"],
        conn_arguments=state["conn_arguments"],
    )
    
    state["judge_comments"].append(comments)
    
    for side , score in updated_score.items():
        state["scores"][side] += score
    
    state["round_no"] += 1
    
    if state["round_no"] > state["max_rounds"]:
        state["debate_over"] = True
    
    return state