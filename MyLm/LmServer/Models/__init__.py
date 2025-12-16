from .. import MODEL_BASE, GLOBAL_CONFIG
def create(model_name: str):
    try:
        import importlib
        _model_name = model_name
        try:
            model_name = model_name.replace("-", "_").replace(".", "_")
            module = importlib.import_module(f".{model_name}", package=__name__)
        except ImportError:
            model_name = GLOBAL_CONFIG[_model_name]["source"].replace("-", "_").replace(".", "_")
            module = importlib.import_module(f".{model_name}", package=__name__)
        return getattr(module, model_name)(MODEL_BASE)
    except ImportError:
        raise ValueError(f"Unknown model name: {_model_name}")