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

def evaluate_arguements(pro_arguements, conn_arguements):
    
    messages = [
        {"role": "system", "content": judge_agent_prompt()},
        {
            "role": "user",
            "content": f"""
               
                Supporter Arguments:
                {pro_arguements }

                Opponent Arguments:
                {conn_arguements }

                Generate your feedback now.
                """
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.8,       # persuasive but controlled
        max_tokens=300
    )

    print(response.choices[0].message.content.strip())
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    topic = "AI should replace traditional classroom teaching"

    pro_arguements = [
        "Human teachers provide emotional intelligence.",
        "AI lacks real-world classroom experience."
    ]

    conn_arguements = [
    "AI can provide personalized learning at scale.",
    "AI systems can be trained using vast real-world classroom data."
    ]


    output = evaluate_arguements(
        pro_arguements=pro_arguements,
        conn_arguements=conn_arguements
    )

    print("\n🟢 JUDGE COMMENT:\n")
    
    print(output)
    