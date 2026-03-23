def load_system_prompt():
    with open("prompts/system.txt", "r", encoding="utf-8") as f:
        return f.read()