from flask import Blueprint, render_template

bp = Blueprint("index", __name__)

@bp.route("/")
def main():
    return render_template("pages/index.html")