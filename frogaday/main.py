from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_user import login_required, current_user

import datetime

from . import db
from .models import User, Goal

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET", "POST"])
def index():
    goal = None
    complete = False
    tz_offset = request.cookies.get("tz_offset", 0)
    date = (
        datetime.datetime.utcnow() - datetime.timedelta(minutes=int(tz_offset))
    ).date()

    if current_user.is_authenticated:
        current_goal = Goal.query.filter_by(user_id=current_user.id, date=date).first()

        if current_goal:
            goal = current_goal.goal
            complete = current_goal.complete

            if request.method == "POST":
                current_goal.complete = not complete
                db.session.commit()

                return redirect(url_for("main.index"))

    return render_template("main/index.html", goal=goal, complete=complete, date=date)
