from __future__ import annotations

from flask import current_app, g
from typing import TYPE_CHECKING
import psycopg2

if TYPE_CHECKING:
    from flask import Flask
    from psycopg2._psycopg import connection as Connection
    from typing import Optional


def get_database() -> Connection:

    if db := g.get("db"):
        return db

    conn: Connection = psycopg2.connect(
        dbname=current_app.config["DB_NAME"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASS"],
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
    )

    g.db = conn
    return conn


def close_database(exc) -> None:
    db: Optional[Connection] = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app: Flask):
    app.teardown_appcontext(close_database)
