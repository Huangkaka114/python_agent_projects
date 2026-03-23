from utils import load_yaml
from AgentFlow.utils import logger
from AgentFlow.tools import get_tools
def check_permission(tool_name: str, user_role: str):
    role_level = {
        "admin": 3,
        "user": 2,
        "guest": 1
    }

    required_level = 1  # 默认最低权限 guest
    tools = get_tools()

    try:
        if tools:
            for tool in tools:
                t_name = tool.name if hasattr(tool, "name") else tool.__name__
                if t_name == tool_name:
                    perm = getattr(tool.func, "permission", "user")
                    required_level = role_level.get(perm, 2)
                    break
        user_level = role_level.get(user_role, 1)
    except Exception as e:
        logger.warn(f"{user_role}权限验证有误")

    return user_level >= required_level