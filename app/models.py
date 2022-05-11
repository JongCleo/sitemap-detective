from flask import Flask
from datetime import datetime
from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.string(120), unique=True, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.email


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.foreignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("jobs", lazy=True))
    # backref creates the mirror property on the User class as "jobs"

    created_at = db.Columns(db.DateTime, nullable=False, server_default=datetime.utcnow)
    celery_id = db.Column(db.Integer)
    # date finished
    # input file
    # output file
    # number of lines in input file

    def __repr__(self):
        return "<Job %r>" % self.id
