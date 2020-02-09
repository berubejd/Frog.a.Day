from flask_user import UserMixin

from datetime import date

from . import db


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column("is_active", db.Boolean(), nullable=False, server_default="1")

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(
        db.String(100), nullable=False, unique=True
    )
    password = db.Column(db.String(255), nullable=False, server_default="")
    email_confirmed_at = db.Column(db.DateTime())

    user_goals = db.relationship("Goal", backref="user")

    def __repr__(self):
        return f"<User {self.username}>"


class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(50))
    complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, default=db.func.current_date(), index=True)

    __table_args__ = (db.UniqueConstraint("user_id", "date", name="_user_date_uc"),)

    def __repr__(self):
        return f"<Goal '{self.goal}'>"
