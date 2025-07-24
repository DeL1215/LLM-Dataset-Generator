import os
import time
from langchain.schema import SystemMessage, HumanMessage
from utils import load_prompt

# 建立輸出目錄與檔案
timestamp = time.strftime("%Y%m%d-%H%M%S")
filename = f"outputs/dataset-{timestamp}.txt"
os.makedirs("outputs", exist_ok=True)

# === 動態切換 LLM 模型 ===
LLM_ = None

def set_llm(llm_instance):
    """
    設定目前要使用的語言模型
    """
    global LLM_
    LLM_ = llm_instance

def generate_and_stream(example: str, addtional: str, num: int) -> int:
    """
    每次呼叫產生 num 筆資料，每筆立即 append 到 dataset 檔案。
    傳回實際產生的筆數（理論上 = num）
    """
    if LLM_ is None:
        raise ValueError("❌ 尚未設定語言模型（LLM）")

    # 建構 prompt 並替換參數
    replacements = {
        "example": example,
        "additional": addtional,
        "num": num
    }

    prompt_text = load_prompt("prompts/mainprompt.txt", replacements)
    messages = [
        SystemMessage(content=prompt_text),
        HumanMessage(content="產生指定數量資料")
    ]

    # 調用 LLM
    response = LLM_.invoke(messages)
    raw_output = response.content.strip()
    cleaned = raw_output.strip().lstrip('[').rstrip(']')

    # 拆解每筆 JSON 資料
    data_parts = [item.strip() for item in cleaned.split("},") if item.strip()]
    final_parts = []

    for part in data_parts:
        if not part.endswith("}"):
            part += "}"
        final_parts.append(part)

    # 寫入檔案
    with open(filename, "a", encoding="utf-8") as f:
        for line in final_parts:
            f.write(line + ",\n")

    return len(final_parts), prompt_text
