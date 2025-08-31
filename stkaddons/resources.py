from flask import Blueprint, redirect

bp = Blueprint("resources", __name__)


@bp.route("/favicon.ico")
def favicon():
    return redirect("/static/icon.png", code=308)


@bp.route("/robots.txt")
def robots_file():
    return redirect("/static/robots.txt", code=308)
