class AgentFlowException(Exception):
    pass

class PermissionDeniedError(AgentFlowException):
    def __init__(self):
        super().__init__("权限不足，无法执行该工具")

class ToolNotFoundError(AgentFlowException):
    def __init__(self):
        super().__init__("未找到可用工具")

class LLMCallError(AgentFlowException):
    def __init__(self):
        super().__init__("大模型调用失败，请检查配置")