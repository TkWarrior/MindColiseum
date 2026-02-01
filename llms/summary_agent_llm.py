import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts.summary_agent_prompt import summary_agent_prompt

load_dotenv()
# Initialize client (Groq / OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("GROQ_SUMMARY_AGENT_API_KEY"),
    base_url="https://api.groq.com/openai/v1"  # Groq endpoint
)

def generate_summary(scores , transcript):
    messages = [
        {"role": "system", "content": summary_agent_prompt()},
        {
            "role": "user",
            "content": f"""
                Debate scores:
                {scores}
                Debate transcript:
                {transcript}
                Generate the summary now.
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
                        

#     scores = {
#         "pro": 6,
#         "con": 8
#     }

#     transcript = [
#         {
#             "speaker": "pro",
#             "text": "Remote work improves productivity by eliminating commute time and allowing employees to work during their most focused hours."
#         },
#         {
#             "speaker": "con",
#             "text": "Productivity gains are inconsistent, and remote work often weakens collaboration, mentoring, and team cohesion."
#         },
#         {
#             "speaker": "judge",
#             "text": "Pro presented a clear productivity argument, but lacked supporting data. Con highlighted organizational risks more concretely."
#         },
#         {
#             "speaker": "pro",
#             "text": "Remote tools such as Slack and Zoom replicate much of in-office collaboration while offering flexibility."
#         },
#         {
#             "speaker": "con",
#             "text": "Digital tools cannot fully replace spontaneous discussions and informal learning that occur in physical offices."
#         },
#         {
#             "speaker": "judge",
#             "text": "Both sides addressed collaboration, but Con provided stronger real-world context."
#         }
#         ]

#     output = generate_argument(
#         scores=scores,
#         transcript=transcript 
#     )

#     print("SUMMARY AGENT OUTPUT:\n")

#     print(output)