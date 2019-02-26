import logging
import traceback
from functools import wraps


def try_except_with_logging(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.info(traceback.print_exc())
            raise Exception

    return wrapper


def try_catch_with_callback(callback=None):
    def out_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Exception:
                res = callback()
                logging.error(traceback.format_exc())
            return res

        return wrapper

    return out_wrapper
