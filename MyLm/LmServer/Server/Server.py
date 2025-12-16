def serve(model_name: str):
    import fastapi
    from ..Models import create
    from fastapi import FastAPI
    app = FastAPI()
    model_instance = create(model_name)
    @app.post("/call")
    async def call(input_data: dict):
        return model_instance(input_data)
    # 这个文件的作用是将大模型封装成一个HTTP服务，方便通过网络调用模型进行推理。
    # 这样就可以把大模型集成到各种应用中去，而不需要每次都直接加载模型。
    # 这个文件中使用了FastAPI框架来创建一个简单的HTTP服务器，并定义了一个预测接口。
    # 服务器启动后，监听在127.0.0.1的某个端口，接受HTTP请求，调用模型进行推理，并返回结果。

    @app.get("/name")
    async def name():
        # 这里用于返回模型的名称
        # 以和预期名称比较一下看看这个端口上监听的模型是不是我们想要的
        return model_instance.__class__.__name__

    import uvicorn
    import socket
    host = "127.0.0.1"
    from .. import GLOBAL_CONFIG
    port = GLOBAL_CONFIG[model_name]["port"]

    # 检查端口是否可被绑定
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            raise RuntimeError(f"端口 {port} 在 {host} 已被占用，无法启动服务器。")
    uvicorn.run(app, host="127.0.0.1", port=port)