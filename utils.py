def load_prompt(file_path: str, replacements: dict) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        prompt = f.read()
    
    for key, value in replacements.items():
        prompt = prompt.replace(f"${{{key}}}", str(value))  # 正確格式為 ${key}
    
    return prompt


