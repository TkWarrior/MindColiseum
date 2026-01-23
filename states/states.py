from typing import TypedDict , List , Dict

class DebateState(TypedDict):
    
    debate_topic: str
    round_no : int
    max_rounds : int
    current_agent : str # "pro" or "con"
    pro_arguments : List[str] # List of arguments made by the pro side
    conn_arguments : List[str] # List of arguments made by the con side  
    
    judge_comments : List[str]
    scores : Dict[str, int] # {"pro": score , "con": score} objectively assign scores
    transcript : List[Dict[str , str]] 
    
    debate_over : bool   