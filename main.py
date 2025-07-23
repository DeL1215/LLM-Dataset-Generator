import os
import time
from configuration import LLM_
from langchain.schema import SystemMessage, HumanMessage
from utils import load_prompt

# 初始化一次，建立檔名
timestamp = time.strftime("%Y%m%d-%H%M%S")
filename = f"outputs/dataset-{timestamp}.txt"
os.makedirs("outputs", exist_ok=True)

def generate_and_stream(example: str, addtional: str, num: int) -> int:
    """
    每次呼叫產生 num 筆資料，每筆立即 append 到 dataset 檔案。
    傳回實際產生的筆數（理論上 = num）
    """
    replacements = {
        "example": example,
        "additional": addtional,
        "num": num
    }

    prompt_text = load_prompt("prompts/mainprompt.txt", replacements)
    messages = [
        SystemMessage(content="你是一個資料生成助手"),
        HumanMessage(content=prompt_text)
    ]

    response = LLM_.invoke(messages)
    raw_output = response.content.strip()
    cleaned = raw_output.strip().lstrip('[').rstrip(']')
    
    # 拆解每筆 JSON（用 , 分開）
    data_parts = [item.strip() for item in cleaned.split("},") if item.strip()]
    final_parts = []

    for i, part in enumerate(data_parts):
        # 補上右大括號（若被 split 掉）
        if not part.endswith("}"):
            part += "}"
        final_parts.append(part)

    # Append 每筆
    with open(filename, "a", encoding="utf-8") as f:
        for line in final_parts:
            f.write(line + ",\n")

    return len(final_parts), prompt_text  
