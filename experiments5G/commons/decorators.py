from datetime import datetime

def ignore_self_arg(fn):
    def wrapped(*args, **kwargs):
        return fn(*args[1:], **kwargs)
    return wrapped
