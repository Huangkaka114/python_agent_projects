import json
import os

# 先定义你的路径（确保存在）
ADMIN_MEMORY_PATH = "storage/memory_admin.json"
USER_MEMORY_PATH = "storage/user_memory_user.json"
GUEST_MEMORY_PATH = "storage/memory_guest_.json"

# 确保目录存在
os.makedirs("storage/memory", exist_ok=True)

def save_memory(state, role: str):
    try:
        if role == "admin":
            with open(ADMIN_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, default=str)
        elif role == "user":
            with open(USER_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, default=str)
        elif role == "guest":
            with open(GUEST_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, default=str)
    except Exception as e:
        print(e)

def load_memory(role: str):
    # 1. 先确定文件路径
    if role == "admin":
        path = ADMIN_MEMORY_PATH
    elif role == "user":
        path = USER_MEMORY_PATH
    elif role == "guest":
        path = GUEST_MEMORY_PATH
    else:
        path = USER_MEMORY_PATH

    # 2. 如果文件不存在 / 为空 / 损坏 → 自动初始化
    try:
        # 文件不存在，直接创建并初始化
        if not os.path.exists(path):
            empty_state = {
                "messages": [],
                "user_preference": {},
                "user_role": role
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(empty_state, f, ensure_ascii=False)
            return empty_state

        # 文件存在但为空 → 重置
        if os.path.getsize(path) == 0:
            empty_state = {
                "messages": [],
                "user_preference": {},
                "user_role": role
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(empty_state, f, ensure_ascii=False)
            return empty_state

        # 正常读取
        with open(path, encoding="utf-8") as f:
            state = json.load(f)

        # 确保字段完整（防止旧文件缺失字段）
        if "messages" not in state:
            state["messages"] = []
        if "user_preference" not in state:
            state["user_preference"] = {}
        state["user_role"] = role  # 强制使用当前角色

        return state

    # 捕获所有异常（JSON损坏、权限问题等）→ 重置文件
    except Exception as e:
        empty_state = {
            "messages": [],
            "user_preference": {},
            "user_role": role
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(empty_state, f, ensure_ascii=False)
        return empty_state