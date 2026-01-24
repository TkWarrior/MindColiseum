import os
from openai import OpenAI
from dotenv import load_dotenv
from prompts.pro_agent_prompt import conn_agent_prompt

load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_CONN_AGENT_API_KEY"),
    base_url="https://api.groq.com/openai/v1"  
)

def generate_argument(topic, pro_arguements=None, judge_comments=None):
    messages = [
        {"role": "system", "content": conn_agent_prompt},
        {
            "role": "user",
            "content": f"""
                Debate Topic:
                {topic}

                Pro Arguments:
                {pro_arguements or "None"}

                Judge Feedback:
                {judge_comments or "None"}

                Generate your argument now.
                """
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.8,       
        max_tokens=300
    )

    return response.choices[0].message.content.strip()
