from functools import wraps
import inspect

def try_except(func):
    @wraps(func)
    def wrapper(*args, default=None, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = None
            if args and hasattr(args[0], "logger"):
                logger = args[0].logger
            if logger:
                logger.logger.error(
                    f"Exception in {func.__qualname__}: {e}"
                )
            return default
    return wrapper

def safe_call(method, *args, label=None, default=None, **kwargs):
    try:
        return method(*args, **kwargs)
    except Exception:
        self = getattr(method, "__self__", None)

        logger = (
            getattr(self, "logger", None)
            if self is not None
            else None
        ) or None
        if logger is None:
            return default
        
        frame = inspect.currentframe().f_back
        caller_func = frame.f_code.co_name
        caller_file = frame.f_code.co_filename
        caller_line = frame.f_lineno

        cmd_name = label or getattr(method, "__qualname__", repr(method))

        logger.logger.error(
            "Step failed: %s | called from %s (%s:%d)",
            cmd_name,
            caller_func,
            caller_file,
            caller_line
        )

        return default

