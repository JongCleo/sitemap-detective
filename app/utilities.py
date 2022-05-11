from . import create_app, db
from flask.cli import FlaskGroup

cli = FlaskGroup(create_app())


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
