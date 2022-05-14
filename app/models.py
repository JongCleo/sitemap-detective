from flask import Flask, current_app
from dataclasses import dataclass
from datetime import datetime
from depot.fields.sqlalchemy import UploadedFileField
from . import db


@dataclass
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.email


@dataclass
class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("jobs", lazy=True))
    # backref creates the mirror property on the User class as "jobs"

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    celery_id = db.Column(db.Integer)
    # date finished
    input_file = db.Column(UploadedFileField())
    # output file
    # number of lines in input file

    def __repr__(self):
        return "<Job %r>" % self.id


def get_or_create(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
