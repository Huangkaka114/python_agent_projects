from abc import ABC, abstractmethod

class BaseTool(ABC):
    name: str
    description: str
    permission: str = "user"

    @abstractmethod
    def run(self, *args, **kwargs):
        # * = 一堆值  ** = 一堆键值对 一起写 = 接收任何参数
        pass