import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts.pro_agent_prompt import pro_agent_prompt

load_dotenv()
# Initialize client (Groq / OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("GROQ_PRO_AGENT_API_KEY"),
    base_url="https://api.groq.com/openai/v1"  # Groq endpoint
)

def generate_argument(topic, conn_arguments, judge_comments):
    messages = [
        {"role": "system", "content": pro_agent_prompt()},
        {
            "role": "user",
            "content": f"""
                Debate Topic:
                {topic}

                Opponent Arguments:
                {conn_arguments}

                Judge Feedback:
                {judge_comments}

                Generate your argument now.
                """
        }
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.8,       # persuasive but controlled
        max_tokens=300
    )

    # print(response.choices[0].message.content.strip())
    
    return response.choices[0].message.content.strip()

# if __name__ == "__main__":
#     topic = "AI should replace traditional classroom teaching"

#     conn_arguements = [
#         "Human teachers provide emotional intelligence.",
#         "AI lacks real-world classroom experience."
#     ]

#     judge_comments = [
#         "Provide concrete examples.",
#         "Avoid overgeneralized claims."
#     ]

#     output = generate_argument(
#         topic=topic,
#         conn_arguements=conn_arguements,
#         judge_comments=judge_comments
#     )

#     print("PRO AGENT OUTPUT:\n")
#     print(output)