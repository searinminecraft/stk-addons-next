from flask import (
    Blueprint,
    abort,
    flash,
    request,
    current_app,
    redirect,
    render_template,
)
import logging
import requests

from ..errors import UsernameTaken, EmailTaken
from ..users import User
from ..database import get_database

bp = Blueprint("register", __name__)
log = logging.getLogger("stkaddons.routes.register")


@bp.route("/register", methods=("GET", "POST"))
def main():
    if request.method == "POST":
        f = request.form

        if not all(
            [x in f for x in ("username", "password", "password_confirm", "email")]
        ):
            flash("Invalid request", "error")
            return render_template("pages/register/index.html"), 400

        if f["password"] != f["password_confirm"]:
            flash("Passwords do not match", "error")
            return render_template("pages/register/index.html"), 400

        try:
            User.check_email(f["email"])
            User.check_username(f["username"])
            User.check_password(f["password"])
        except Exception as e:
            log.debug("Failed verification for form: %s", str(e))
            flash(str(e), "error")
            return render_template("pages/register/index.html"), 400

        if not f.get("g-recaptcha-response"):
            flash("Complete the reCAPTCHA verification below", "error")
            return render_template("pages/register/index.html"), 400

        try:
            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": f"STKAddons-Next ({current_app.config['VERSION']}) +https://github.com/searinminecraft/stk-addons-next",
                },
                data=(
                    f"secret={current_app.config['RECAPTCHA_SECRET_KEY']}"
                    f"&response={f['g-recaptcha-response']}"
                    f"&remoteip={request.remote_addr}"
                ),
            )

            json = r.json()
            if not json["success"]:
                log.error("Failure verifying challenge: %s", json)
                flash("Invalid reCAPTCHA response", "error")
                return render_template("pages/register/index.html"), 400
        except Exception:
            log.exception(
                "Unable to connect to reCAPTCHA. Try again or contact the site administrator."
            )
            return render_template("pages/register/index.html"), 500

        try:
            user = User.register(
                f["username"], f["password"], f["email"], f["realname"]
            )
        except (UsernameTaken, EmailTaken) as e:
            flash(str(e), "error")
            return render_template("pages/register/index.html"), 400
        except Exception:
            log.exception("Failure creating user account %s", f["username"])
            flash(
                "Unable to create your user account. Try again later or contact the site administrator.",
                "error",
            )
            return render_template("pages/register/index.html"), 500

        return render_template("pages/register/activation.html", email=f["email"])
    else:
        return render_template("pages/register/index.html")


@bp.route("/confirm_account")
def confirm_account():
    if not request.args.get("code"):
        log.error("User tried to go to confirm_account without code!")
        abort(400)

    db = get_database()
    cur = db.cursor()

    cur.execute("SELECT id FROM verification WHERE code = %s", (request.args["code"],))
    data = cur.fetchone()

    if not data:
        abort(400)

    id = data[0]
    user = User.get_user(id=id)
    user.activate_user()

    return render_template("pages/register/success.html")
