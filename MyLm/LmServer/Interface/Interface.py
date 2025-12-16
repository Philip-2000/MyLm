
def call(model_name: str, content : dict):
    check = content.get("check", True)
    if not check: #only when you are sure the server is running correctly
        import requests
        url = f"http://localhost:{GLOBAL_CONFIG[model_name]['port']}/call"
        
        response = requests.post(url, json={"content": content, **kwargs})
        
        return response.json()

    from .. import GLOBAL_CONFIG
    #通过访问对应端口来调用模型进行推理
    port = GLOBAL_CONFIG[model_name]["port"]
    m_name = model_name.replace("-", "_").replace(".", "_")

    def _build_tmux_tutorial(model_name: str, port: int, error: str) -> str:
        from os.path import dirname as opd
        return (
            f"{error} \n\n"
            f"请使用 tmux 在后台启动模型服务，示例步骤（请根据你的环境替换路径和命令）：\n"
            f"1) tn {model_name} /  ta {model_name}\n\n"
            f"2) tca {GLOBAL_CONFIG[model_name]['env']} && source {opd(opd(opd(opd(__file__))))}/scripts/LmServe/LmServe/{m_name}.sh\n\n"
        )


    # 检查端口是否有服务在监听（若未被占用则报错退出）
    import socket, requests
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        sock.connect(("127.0.0.1", port))
    except Exception:
        raise RuntimeError(_build_tmux_tutorial(model_name, port, f"预期端口 {port} 上没有检测到任何活动服务。"))
    finally:
        sock.close()

    # 检查 /name 接口返回的模型名是否与期望一致
    try:
        resp = requests.get(f"http://127.0.0.1:{port}/name", timeout=2.0)
        resp.raise_for_status()
        try:
            reported = resp.json()
        except ValueError:
            reported = resp.text.strip()
    except Exception:
        raise RuntimeError(_build_tmux_tutorial(model_name, port, f"无法从模型服务获取模型名称，可能服务未正确启动或响应异常。"))

    
    if reported != m_name:
        msg = (
            f"服务返回的模型名与期望不一致：期望 '{m_name}'，但服务返回 '{reported}'.\n\n"
            + _build_tmux_tutorial(model_name, port, "请检查是否启动了正确的模型服务。")
        )
        raise RuntimeError(msg)
    import requests
    url = f"http://localhost:{port}/call"
    response = requests.post(url, json=content)
    
    
    return response.json()