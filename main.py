from graph.graph import agent

if __name__ == "__main__":
    
    user_input = input("Enter the debate topic: ")
    
    initial_state = {
        "debate_topic": user_input,
        "round_no": 1,
        "max_rounds": 3,
        "current_agent": "pro_agent",
        "pro_arguments" : [] ,# List of arguments made by the pro side
        "conn_arguments" : [] ,# List of arguments made by the con side  
        "judge_comments" : [] ,
        "scores" : {"pro":0 , "con":0} ,# {"pro": score , "con": score} objectively assign scores
        "transcript" : [] , 
        "debate_over" : False      
    }
    
    agent.invoke(initial_state)
    
    print("agent:",agent)
