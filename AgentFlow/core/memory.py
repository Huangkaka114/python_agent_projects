import json
import os

ADMIN_MEMORY_PATH = "storage/memory_admin.json"
USER_MEMORY_PATH = "storage/memory_user.json"
GUEST_MEMORY_PATH = "storage/memory_guest.json"

# 把state按json存入本地
def save_memory(state, role: str):
    if role == "admin":
        with open(ADMIN_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, default=str)
    elif role == "user":
        with open(USER_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, default=str)
    elif role == "guest":
        with open(GUEST_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, default=str)

def load_memory(role: str):
    try:
        if role == "admin":
            with open(ADMIN_MEMORY_PATH, encoding="utf-8") as f:
                return json.load(f)
        elif role == "user":
            with open(USER_MEMORY_PATH, encoding="utf-8") as f:
                return json.load(f)
        elif role == "guest":
            with open(GUEST_MEMORY_PATH, encoding="utf-8") as f:
                return json.load(f)
    except:
        # 修复：文件损坏直接返回默认值
        return {"messages": [], "user_preference": {}, "user_role": "user"}