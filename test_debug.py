"""Quick debug script to test agent.invoke and find where it crashes."""
import sys, traceback
sys.path.insert(0, '.')
from graph.graph import agent

initial_state = {
    'debate_topic': 'Is remote work better than office work?',
    'round_no': 1,
    'max_rounds': 1,
    'current_agent': 'pro_agent',
    'pro_arguments': [],
    'conn_arguments': [],
    'judge_comments': [],
    'scores': {'pro': 0, 'con': 0},
    'round_scores': [],
    'transcript': [],
    'debate_over': False,
}

try:
    print("Starting agent.invoke()...")
    result = agent.invoke(initial_state)
    print("SUCCESS! agent.invoke() completed.")
    print("=" * 50)
    print("Result keys:", list(result.keys()))
    print("Scores:", result.get('scores'))
    print("Round scores:", result.get('round_scores'))
    print("Pro args count:", len(result.get('pro_arguments', [])))
    print("Con args count:", len(result.get('conn_arguments', [])))
    print("Judge comments count:", len(result.get('judge_comments', [])))
    
    transcript = result.get('transcript', [])
    print(f"Transcript entries: {len(transcript)}")
    for i, entry in enumerate(transcript):
        entry_type = type(entry).__name__
        print(f"  [{i}] type={entry_type}")
        if hasattr(entry, 'content'):
            print(f"       .content = {str(entry.content)[:100]}...")
        elif isinstance(entry, dict):
            content = entry.get('content', 'N/A')
            print(f"       content = {str(content)[:100]}...")
    
    # Now simulate the DB save logic from _run_debate_async
    print("=" * 50)
    print("Simulating DB save logic...")
    
    pro_args = result.get("pro_arguments", [])
    con_args = result.get("conn_arguments", [])
    judge_comments = result.get("judge_comments", [])
    round_scores = result.get("round_scores", [])
    
    num_rounds = max(len(pro_args), len(con_args))
    print(f"num_rounds: {num_rounds}")
    
    for i in range(num_rounds):
        round_score = round_scores[i] if i < len(round_scores) else {"pro": 0, "con": 0}
        pro_s = round_score.get("pro", 0)
        con_s = round_score.get("con", 0)
        print(f"  Round {i+1}: pro_score={pro_s} (type={type(pro_s).__name__}), con_score={con_s} (type={type(con_s).__name__})")
    
    scores = result.get("scores", {"pro": 0, "con": 0})
    print(f"Final scores: {scores}")
    print(f"  pro type: {type(scores.get('pro', 0)).__name__}")
    print(f"  con type: {type(scores.get('con', 0)).__name__}")
    
    # Check summary extraction
    print("=" * 50)
    print("Simulating summary extraction...")
    for entry in reversed(transcript):
        if hasattr(entry, 'content'):
            content = entry.content
        elif isinstance(entry, dict):
            content = entry.get("content", "")
        else:
            content = str(entry)
        
        if "[SUMMARY]" in content:
            summary = content.replace("[SUMMARY]", "").strip()
            print(f"Found summary: {summary[:100]}...")
            break
    else:
        print("No [SUMMARY] tag found in transcript!")
    
    print("=" * 50)
    print("ALL CHECKS PASSED")

except Exception as e:
    print(f"FAILED: {e}")
    traceback.print_exc()
