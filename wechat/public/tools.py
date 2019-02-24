from functools import wraps

from flask import render_template


def message_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return render_template('{}.html'.format(res.get('MsgType')), **res)

    return wrapper
