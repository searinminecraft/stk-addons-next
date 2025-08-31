from __future__ import annotations

from . import database
from .errors import (
    UsernameLengthError,
    PasswordLengthError,
    InvalidUsername,
    InvalidEmail,
    BadPassword,
    EmailTaken,
    UsernameTaken,
    DatabaseError,
)

import datetime
from psycopg2 import Error as PgError
import re
from typing import TYPE_CHECKING, Optional
from werkzeug.security import generate_password_hash

from . import util

if TYPE_CHECKING:
    from psycopg2._psycopg import (
        cursor as Cursor,
    )

USERNAME_RE = re.compile(r"^[a-zA-Z0-9\.\-\_]+$")
PASSWORD_RE = re.compile(
    r"^[a-zA-Z0-9\!\@\#\$\%\^\&\*\(\)\_\+\=\-\/\\\{\}\~\>\<\'\;\[\]\,\.\"\|\`]+$"
)
EMAIL_RE = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
)


class Role:
    def __init__(self, id, name, display_name):
        self.id: int = id
        self.name: str = name
        self.display_name: Optional[str] = display_name


class User:
    def __init__(
        self,
        id,
        username,
        role_id,
        password,
        realname,
        email,
        date_login,
        date_register,
        homepage,
        activated,
    ):
        self.id: int = id
        self.username: str = username
        self.role_id: int = role_id
        self.password: str = password
        self.realname: str = realname or username
        self.email: str = email
        self.date_login: datetime.datetime = date_login
        self.date_register: datetime.datetime = date_register
        self.homepage: Optional[str] = homepage
        self.activated: bool = activated

    @classmethod
    def get_user(cls, *, id: int = None, username: str = None) -> Optional[User]:
        print(id, username  )
        if id is None and username is None:
            raise ValueError("Provide a username or ID")

        db = database.get_database()
        cur: Cursor = db.cursor()

        if id:
            cur.execute("SELECT * FROM users WHERE id = %s", (int(id),))
        elif username:
            cur.execute("SELECT * FROM users WHERE username LIKE %s", (username,))
        else:
            raise ValueError("Provide a username or ID")

        res = cur.fetchone()

        if not res:
            return None

        return cls(*res)

    @classmethod
    def register(cls, username, password, email, realname: Optional[str] = None):
        db = database.get_database()
        cur: Cursor = db.cursor()

        try:
            cur.execute(
                """
                INSERT INTO users
                (username, password, realname, email)
                VALUES
                (%(username)s, %(password)s, %(realname)s, %(email)s)
                RETURNING id
                """,
                {
                    "username": username,
                    "password": str(generate_password_hash(password)),
                    "realname": realname,
                    "email": email,
                },
            )
        except PgError as e:
            if e.diag.constraint_name == "user_unique_email":
                raise EmailTaken
            if e.diag.constraint_name == "user_unique_username":
                raise UsernameTaken

            raise DatabaseError(
                "A database error occurred while trying to register"
            ) from e

        id = cur.fetchone()[0]
        db.commit()
        print(id)

        cls.set_verification(id)

        from . import stk_mail

        stk_mail.send_new_account_verification(id)

    @staticmethod
    def set_verification(id):
        """Set a verification code for the User"""

        db = database.get_database()
        cur = db.cursor()

        cur.execute(
            "INSERT INTO verification VALUES (%(id)s, %(code)s)",
            {"id": id, "code": util.random_string(50)},
        )
        db.commit()

    @property
    def role(self) -> Role:
        db = database.get_database()
        with db.cursor() as cur:
            cur.execute(
                "SELECT * FROM roles WHERE id = %(id)s", {"id": self.id}
            )
            data = cur.fetchone()
            return Role(*data)

    @property
    def achievements(self):
        db = database.get_database()
        cur: Cursor = db.cursor()

        cur.execute(
            "SELECT achievement_id FROM achieved WHERE id = %(id)s", {"id": self.id}
        )
        data = cur.fetchall()

        return [x[0] for x in data]

    @staticmethod
    def check_username(username: str):
        """Checks Username for validity"""
        if len(username) < 3 or len(username) > 30:
            raise UsernameLengthError

        if not USERNAME_RE.search(username):
            raise InvalidUsername

    @staticmethod
    def check_password(password: str):
        """Checks password for validity"""
        if len(password) < 8 or len(password) > 64:
            raise PasswordLengthError

        if not PASSWORD_RE.search(password):
            raise BadPassword

    @staticmethod
    def check_email(email: str):
        """Checks email for validity"""
        if not EMAIL_RE.search(email):
            raise InvalidEmail

    def activate_user(self):
        """Activates the user, allowing it to be used"""

        db = database.get_database()
        cur: Cursor = db.cursor()

        try:
            cur.execute("UPDATE users SET activated = true WHERE id = %s", (self.id,))
            cur.execute("DELETE FROM verification WHERE id = %s", (self.id,))
            db.commit()
        except PgError as e:
            db.rollback()
            raise DatabaseError(
                "A database error occurred while trying to activate your account"
            ) from e

