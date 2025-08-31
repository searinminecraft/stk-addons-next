from flask import Blueprint, Response, current_app
import logging
from xml.etree import ElementTree as et

from ..errors import UserException
from .users import bp as users
from ..util import generic_response

bp = Blueprint("api", __name__, url_prefix="/api/v2")
log = logging.getLogger("stkaddons.api")

bp.register_blueprint(users)


@bp.errorhandler(Exception)
def handle_exception(e: Exception):
    if isinstance(e, UserException):
        return generic_response(success=False, info=str(e))

    log.exception("Unhandled exception in request")
    return generic_response(success=False, info=f"Exception Error: {str(e)}")


@bp.after_request
def set_appropriate_headers(r: Response):
    r.headers["Content-Type"] = "application/xml"
    return r


@bp.route("/version/", methods=("GET", "POST"))
def version():
    e = et.Element(
        "api", {"success": "yes", "version": current_app.config["VERSION"], "info": ""}
    )
    return et.tostring(e)
