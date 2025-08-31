from __future__ import annotations
from flask import request
import datetime
from typing import TYPE_CHECKING
from werkzeug.security import check_password_hash

from .database import get_database
from .errors import InvalidCredentials, InvalidSession, UserNotFound
from . import util
from .users import User


class ClientSession:
    def __init__(self, session_id: str, user: User):
        self.session_id = session_id
        self.user: User = user

    @classmethod
    def create(
        cls, username: str, password: str, save_session: bool = False
    ) -> ClientSession:
        """Create a new Client Session with provided credentials"""
        if not username or not password:
            raise InvalidCredentials

        user = User.get_user(username=username)

        if not user:
            raise InvalidCredentials

        check = check_password_hash(user.password, password)
        if not check:
            raise InvalidCredentials

        token_str = util.random_string()

        db = get_database()
        cur = db.cursor()

        cur.execute(
            """
            INSERT INTO sessions (id, token, user_agent)
            VALUES (%(id)s, %(token)s, %(ua)s)
            """,
            {"id": user.id, "token": token_str, "ua": request.user_agent.string},
        )
        cur.execute(
            """
            UPDATE users SET date_login = %s WHERE id = %s
            """,
            (datetime.datetime.now(), user.id),
        )
        db.commit()

        return cls(token_str, user)

    @classmethod
    def get(cls, id: str, token: str) -> ClientSession:
        """Get a session"""
        user = User.get_user(id)

        if not user:
            raise UserNotFound

        db = get_database()
        cur = db.cursor()

        cur.execute("SELECT token, last_login FROM sessions WHERE id = %s", (user.id,))
        data = cur.fetchall()

        if not data:
            raise InvalidSession

        if token not in [x[0] for x in data]:
            raise InvalidSession

        return cls(token, user)

    def poll(self):
        """Poll server for activity status and notifications"""

        db = get_database()
        cur = db.cursor()

        cur.execute(
            "UPDATE sessions SET last_activity = %s WHERE id = %s",
            (datetime.datetime.now(), self.user.id),
        )
        db.commit()
