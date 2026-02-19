import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts.judge_agent_prompt import judge_agent_prompt

load_dotenv()
# Initialize client (Groq / OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("GROQ_JUDGE_AGENT_API_KEY"),
    base_url="https://api.groq.com/openai/v1"  # Groq endpoint
)

def evaluate_arguments(pro_arguments, conn_arguments):
    
    messages = [
        {"role": "system", "content": judge_agent_prompt()},
        {
            "role": "user",
            "content": f"""
               
                Supporter Arguments:
                {pro_arguments }

                Opponent Arguments:
                {conn_arguments }

                Generate your feedback now.
                """
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.8,       # persuasive but controlled
        max_tokens=300
    )
    raw = response.choices[0].message.content.strip()
    
    # LLMs often wrap JSON in markdown code fences — strip them
    if raw.startswith("```"):
        # Remove ```json or ``` prefix and trailing ```
        lines = raw.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw = "\n".join(lines).strip()
    
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: if LLM returns invalid JSON, return safe defaults
        print(f"[JUDGE] Failed to parse JSON from LLM response: {raw[:200]}")
        return "Judge could not parse scores this round.", {"pro": 0, "con": 0}
    
    result = parsed["comments"], parsed["updated_score"]
    return result

# if __name__ == "__main__":
#     topic = "AI should replace traditional classroom teaching"

#     pro_arguements = [
#         "Human teachers provide emotional intelligence.",
#         "AI lacks real-world classroom experience."
#     ]

#     conn_arguements = [
#     "AI can provide personalized learning at scale.",
#     "AI systems can be trained using vast real-world classroom data."
#     ]


#     output = evaluate_arguements(
#         pro_arguements=pro_arguements,
#         conn_arguements=conn_arguements
#     )

#     print("JUDGE COMMENT:\n")
    
#     print(output)
    