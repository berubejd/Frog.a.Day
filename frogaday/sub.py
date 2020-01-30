from flask import (
    Blueprint,
    escape,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_user import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

import calendar
import datetime

from bs4 import BeautifulSoup as Soup

from . import db
from .models import User, Goal


bp = Blueprint("sub", __name__)


def calendar_update_header(soup, current=True):
    """ Find first table row and:
        1. add buttons, if appropriate
        2. shrink month header to only span middle 5 columns 
        
        return soup"""

    # Shrink month header
    elem = soup.select_one("th.month")
    elem["colspan"] = 5

    # Set the prev/next buttons
    # Previous month button
    pm_tag = soup.new_tag("th")

    if current:
        pm_link = soup.new_tag("a", href=f"{ url_for('sub.cal_prev') }")
        pm_link.string = "<"

        pm_tag.append(pm_link)
    else:
        pm_tag.string = ""

    elem.insert_before(pm_tag)

    # Next month button
    nm_tag = soup.new_tag("th")

    if not current:
        nm_link = soup.new_tag("a", href=f"{ url_for('sub.cal_curr') }")
        nm_link.string = ">"

        nm_tag.append(nm_link)
    else:
        nm_tag.string = ""

    elem.insert_after(nm_tag)

    return soup


def calendar_update_goals(soup, year, month):
    """ Loop over monthly Goal entries and:
        1. Find correct table cell for the day
        2. Add span with class 'tooltiptext' and text of escaped goal
        3. Add 'tooltip' class
        4. Add 'complete' or 'not-complete' class

        return soup """

    goals = (
        Goal.query.filter(Goal.user_id == current_user.id)
        .filter(db.extract("year", Goal.date) == year)
        .filter(db.extract("month", Goal.date) == month)
        .all()
    )

    for goal in goals:
        elem = soup.find(text=goal.date.day)

        goal_tag = soup.new_tag("span")
        goal_tag["class"] = ["tooltiptext"]
        goal_tag.string = escape(goal.goal)
        elem.insert_after(goal_tag)

        complete = ["complete"] if goal.complete else ["not-complete"]

        parent = elem.parent
        parent["class"] = parent["class"] + ["tooltip"] + complete

    return soup


@bp.route("/calendar")
@login_required
def cal_curr():
    tz_offset = request.cookies.get("tz_offset", 0)
    date = (
        datetime.datetime.utcnow() - datetime.timedelta(minutes=int(tz_offset))
    ).date()

    day = date.day
    month = date.month
    year = date.year

    cal_html = calendar.HTMLCalendar(firstweekday=6).formatmonth(
        theyear=year, themonth=month
    )

    soup = Soup(cal_html, "html.parser")

    # Update calendar header
    soup = calendar_update_header(soup, current=True)

    # Find today and add 'today' class
    elem = soup.find(text=day).parent
    elem["class"] = elem["class"] + ["today"]

    # Update calendar with goal data
    soup = calendar_update_goals(soup, year, month)

    return render_template("sub/calendar.html", calendar_table=soup.prettify())


@bp.route("/calendar-previous")
@login_required
def cal_prev():
    tz_offset = request.cookies.get("tz_offset", 0)
    date = (
        datetime.datetime.utcnow() - datetime.timedelta(minutes=int(tz_offset))
    ).date()

    # Hack for lack of timedelta handling of months
    date = date.replace(day=1)
    date = date - datetime.timedelta(days=1)

    day = date.day
    month = date.month
    year = date.year

    cal_html = calendar.HTMLCalendar(firstweekday=6).formatmonth(
        theyear=year, themonth=month
    )

    soup = Soup(cal_html, "html.parser")

    # Update calendar header
    soup = calendar_update_header(soup, current=False)

    # Update calendar with goal data
    soup = calendar_update_goals(soup, year, month)

    return render_template("sub/calendar.html", calendar_table=soup.prettify())


@bp.route("/about")
def about():
    return render_template("sub/about.html")


@bp.route("/congrats")
def congrats():
    return render_template("sub/congrats.html")


class EditForm(FlaskForm):
    goal = StringField(
        "Today's Goal:",
        [DataRequired(), Length(min=3, max=50, message="Please include a goal of between 3 and 50 characters.")],
    )
    submit = SubmitField("Submit")


@bp.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    tz_offset = request.cookies.get("tz_offset", 0)
    date = (
        datetime.datetime.utcnow() - datetime.timedelta(minutes=int(tz_offset))
    ).date()

    form = EditForm()

    # Check for a current entry in the DB
    current_goal = Goal.query.filter_by(user_id=current_user.id, date=date).first()

    # Perform form validation and DB update
    if form.validate_on_submit():

        # No goal for today exists so create a new entry
        if not current_goal:
            new_goal = Goal(goal=form.goal.data, user_id=current_user.id, date=date)
            db.session.add(new_goal)

        else:
            # A goal already exists to update it
            current_goal.goal = form.goal.data

        db.session.commit()

        return redirect(url_for("main.index"))

    # This isn't an update so prepopulate the form if a goal exists
    if current_goal:

        if current_goal.complete:
            return redirect(url_for("sub.congrats"))

        form.goal.data = current_goal.goal

    return render_template("sub/edit.html", form=form)
