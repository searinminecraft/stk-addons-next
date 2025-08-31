from __future__ import annotations

from flask import Blueprint, current_app, request
import logging
from typing import TYPE_CHECKING
from xml.etree import ElementTree as et

from ..users import User
from ..client_session import ClientSession
from ..util import generic_response, need_client_session

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableMultiDict

bp = Blueprint("api_users", __name__, url_prefix="/user")
log = logging.getLogger("stkaddons.api.user")


@bp.post("/register/")
def register():
    f: ImmutableMultiDict = request.form
    scope = "registration"

    if current_app.config.get("DISABLE_REGISTRATION_FROM_STK") == True:
        return (
            generic_response(
                scope,
                False,
                (
                    "Registration from the game client has been "
                    "disabled. Please use the website instead."
                ),
            ),
            403,
        )

    username = f.get("username")
    password = f.get("password")
    password_confirm = f.get("password_confirm")
    realname = f.get("realname")
    email = f.get("email")
    terms = f.get("terms") == "on"

    if not username:
        return generic_response(scope, False, "Username required"), 400

    if not password:
        return generic_response(scope, False, "Password required"), 400

    try:
        User.check_username(username)
        User.check_password(password)
    except Exception as e:
        log.exception("Validation error")
        return generic_response(scope, False, str(e)), 400

    if not password_confirm or password != password_confirm:
        return generic_response(scope, False, "Passwords don't match"), 400

    if not email:
        return generic_response(scope, False, "Email required"), 400

    try:
        User.check_email(email)
    except Exception as e:
        return generic_response(scope, False, str(e)), 400

    if not terms:
        return (
            generic_response(scope, False, "You must agree to the terms to register"),
            400,
        )

    User.register(username, password, email, realname)

    return generic_response(scope)


@bp.post("/connect/")
def login():
    f: ImmutableMultiDict = request.form
    session = ClientSession.create(f.get("username"), f.get("password"))
    e = et.Element(
        "connect",
        {
            "success": "yes",
            "token": session.session_id,
            "username": session.user.username,
            "realname": session.user.realname,
            "userid": str(session.user.id),
            "achieved": " ".join(session.user.achievements),
        },
    )
    return et.tostring(e)


@bp.post("/saved_session/")
@need_client_session
def saved_session(session: ClientSession):
    e = et.Element(
        "saved-session",
        {
            "success": "yes",
            "token": session.session_id,
            "username": session.user.username,
            "realname": session.user.realname,
            "userid": str(session.user.id),
            "achieved": " ".join(session.user.achievements),
        },
    )
    return et.tostring(e)


@bp.post("/poll/")
@need_client_session
def poll(session: ClientSession):
    session.poll()
    return generic_response("poll", True)
