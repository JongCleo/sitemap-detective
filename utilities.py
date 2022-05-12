from flask.cli import FlaskGroup
from app import create_app, db

app_instance = create_app()
cli = FlaskGroup(app_instance)


@cli.command("create_db")
def create_db():
    with app_instance.app_context():
        print(db)
        db.drop_all()
        db.create_all()
        db.session.commit()


if __name__ == "__main__":
    cli()
