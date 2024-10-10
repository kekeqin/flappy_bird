
START = 0  # 表示游戏开始事件定义为常量0
JOIN = 1   # 表示玩家加入事件定义为常量1
JUMP = 2   # 表示玩家跳跃事件定义为常量2
SCORE = 3  # 表示玩家分数事件定义为常量3
DIED = 4   # 表示玩家死亡事件定义为常量4
PLAYER_LIST = 5  # 表示玩家列表事件定义为常量5
QUIT = 6   # 表示客户端退出事件定义为常量6
CLIENT_QUIT = 7
READY = 8 

PIPE_DATA = 9

# 定义一个Event类，用于表示游戏中的事件
class Event:
    def __init__(self, id, data): # 使用init构造方法初始化事件，放入属性id和data
        self.id = id   # 事件的id，对应定义的常量
        self.data = data  # 事件的数据，可以是任何与事件相关的信息

    # 定义isEvent函数，用于检查事件是否为特定类型
    def isEvent(self, target):
        return self.id == target # 如果当前事件id与目标id一致，则返回True


    # 定义一个to_dict方法，用于将事件对象转换为字典格式
    def to_dict(self):
        return {"id": self.id, "data": self.data}  # 返回一个包含事件id和data的字典
    


# 示例
# event = Event(id=SCORE, data={"score: 10})
# event =Event(id=START)
