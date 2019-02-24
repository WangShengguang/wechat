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
