class AFormater:
    def __init__(self):
        pass

    def video(self, v):
        pass
    
    def text(self, t):
        pass

    def image(self, i):
        pass

class AModel:
    # 这个类用于规范化模型的接口和行为，使得各种不同的模型的使用更加统一和简便。
    # 一般来说，初始化都用__init__方法，调用都用__call__方法。不过原本模型由于使用的库可能略有不一样，所以他们不是完全统一的
    # 但是我们这里可以把他们封装成统一的接口。

    def __call__(self, input_data):
        #input_data : dict
            #input_data["content"]: list
            # Each value in "content" has to be a list of dicts with types ("text", "image", "video")
        pass
        # 这个方法用于调用模型进行推理，输入是input_data，输出是模型的预测结果。
        # 具体的实现会根据不同的模型有所不同，但是接口是一致的。