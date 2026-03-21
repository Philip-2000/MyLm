
def call(model_name: str, content : dict):
    from .. import GLOBAL_CONFIG, ONLINE_CONFIG
    import socket, requests

    if model_name in ONLINE_CONFIG.keys():
        import importlib
        online = importlib.import_module("MyLm.LmServer.Interface.online")
        func = getattr(online, model_name.replace("-", "_"))
        return func(content)

    check = content.get("check", True)
    if not check: #only when you are sure the server is running correctly
        url = f"http://localhost:{GLOBAL_CONFIG[model_name]['port']}/call"
        
        response = requests.post(url, json=content)
        
        return response.json()

    #通过访问对应端口来调用模型进行推理
    requested = GLOBAL_CONFIG[model_name]
    prefix = requested["name"].split(":")[0]
    m_name = model_name.replace("-", "_").replace(".", "_").split(":")[0]

    def _build_tmux_tutorial(model_name: str, port: int, error: str) -> str:
        from os.path import dirname as opd
        return (
            f"{error} \n\n"
            f"请使用 tmux 在后台启动模型服务，示例步骤（请根据你的环境替换路径和命令）：\n"
            f"1) tn {model_name} /  ta {model_name}\n\n"
            f"2) tca {GLOBAL_CONFIG[model_name]['env']} && source {opd(opd(opd(opd(__file__))))}/scripts/LmServe/LmServe/{m_name}.sh\n\n"
        )


    # 找到所有同前缀的副本，并按照请求顺序排列（先尝试目标副本，再逐一尝试其他副本）
    replicas = [
        conf for conf in GLOBAL_CONFIG.config
        if conf["name"].split(":")[0] == prefix
    ]
    ordered_replicas = []
    if requested in replicas:
        ordered_replicas.append(requested)
    ordered_replicas.extend(conf for conf in sorted(replicas, key=lambda conf: conf["port"]) if conf not in ordered_replicas)

    selected_conf = None
    last_error = ""
    for conf in ordered_replicas:
        port = conf["port"]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        try:
            sock.connect(("127.0.0.1", port))
        except Exception as exc:
            last_error = f"端口 {port} 未响应：{exc}"
            continue
        finally:
            sock.close()

        try:
            resp = requests.get(f"http://127.0.0.1:{port}/name", timeout=2.0)
            resp.raise_for_status()
            try:
                reported = resp.json()
            except ValueError:
                reported = resp.text.strip()
        except Exception as exc:
            last_error = f"无法从端口 {port} 获取模型名称：{exc}"
            continue

        if reported != m_name:
            last_error = f"端口 {port} 返回的模型名 {reported} 与期望 {m_name} 不符。"
            continue

        selected_conf = conf
        break

    if selected_conf is None:
        hint = last_error or "未检测到任何可用的模型服务。"
        raise RuntimeError(_build_tmux_tutorial(model_name, requested["port"], hint))
    url = f"http://localhost:{selected_conf['port']}/call"
    response = requests.post(url, json=content)
    # print("Response Status Code:", response.status_code)
    
    return response.json()