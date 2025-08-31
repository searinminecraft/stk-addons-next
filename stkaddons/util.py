from .errors import InvalidSession
from functools import wraps
from flask import request
import string
import random
from xml.etree import ElementTree as et


def generic_response(scope: str = "api", success: bool = True, info: str = "") -> str:
    """Return a generic response which does not contain additional data"""
    element = et.Element(scope, {"success": "yes" if success else "no", "info": info})
    return et.tostring(element)


def random_string(length: int = 30):
    """Generate a random string with desired length (default 30)"""
    return "".join([random.choice(string.ascii_letters) for x in range(length)])


def need_client_session(f):
    from .client_session import ClientSession

    @wraps(f)
    def wrapped(**kwargs):
        f = request.form
        session = ClientSession.create(f["userid"], f["token"])

        return f(session, **kwargs)
    
    return wrapped
