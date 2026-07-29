__all__ = ["app", "create_app"]


def __getattr__(name):
    if name not in __all__:
        raise AttributeError(name)
    from .main import app, create_app

    return {"app": app, "create_app": create_app}[name]