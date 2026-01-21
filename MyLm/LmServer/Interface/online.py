from openai import OpenAI
from .. import ONLINE_CONFIG

Qwen3_Ours_Client = OpenAI(base_url=ONLINE_CONFIG["Qwen3-Ours"]["base_url"], api_key=ONLINE_CONFIG["Qwen3-Ours"]["api_key"])

def Qwen3_Ours(input_data: dict):
    completion = Qwen3_Ours_Client.chat.completions.create(
        model=ONLINE_CONFIG["Qwen3-Ours"]["model"],
        messages = [
            {"role":k, "content":v} for item in input_data["content"] for k,v in item.items() 
        ]
    )
    return completion.choices[0].message.content