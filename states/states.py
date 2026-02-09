from typing import TypedDict ,Annotated, List , Dict
from langgraph.graph import add_messages

class DebateState(TypedDict):
    
    debate_topic: str
    round_no : int
    max_rounds : int
    current_agent : str # "pro" or "con"
    pro_arguments : List[str] # List of arguments made by the pro side
    conn_arguments : List[str] # List of arguments made by the con side  
    
    judge_comments : List[str]
    scores : Dict[str, int] # {"pro": score , "con": score} cumulative scores
    round_scores : List[Dict[str, int]]  # Per-round scores: [{"pro": 1, "con": 0}, ...]
    transcript : Annotated[List[Dict[str , str]] , add_messages] 
    
    debate_over : bool   