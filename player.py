
# 定义一个player类，用于表示游戏中的玩家
class Player:
    def __init__(self, pid): # 使用init构造方法，放入属性pid
        self.pid = pid  # 玩家的标识符


    # 定义一个to_dict函数，用于将玩家对象转换为字典格式
    def to_dict(self):
        return {"pid": f'p{self.pid}'} # 返回一个包含玩家pid的字典，pid前加上前缀‘p’
