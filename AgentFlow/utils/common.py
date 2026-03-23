import yaml

def load_yaml(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_user_role(state):
    return state.get("user_role", "user")