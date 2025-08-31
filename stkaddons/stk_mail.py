from flask import render_template
from flask_mail import Mail, Message
from .database import get_database
from .users import User

def send_new_account_verification(id) -> None:
    db = get_database()
    cur = db.cursor()
    mail = Mail()

    user = User.get_user(id=id)

    cur.execute("SELECT code FROM verification WHERE id = %s", (id,))
    code = cur.fetchone()[0]

    message = Message(
        subject="New SuperTuxKart Account",
        recipients=[user.email],
        html=render_template("mail/new_account.html", user=user, code=code)
    )
    mail.send(message)
