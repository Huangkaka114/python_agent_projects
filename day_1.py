class SimpleAgent:
    def __init__(self,name):
        self.name = name
        # self必须是第一个参数，代表当前创建的那个对象本身 即this
    def talk(self,text):
            return f"{self.name}: {text}"
agent = SimpleAgent("我的第一个agent")
print(agent.talk("你好"))