from os import path
import pytest
from app import create_app, db as database


@pytest.fixture(scope="session")
def app():

    app = create_app()

    with app.app_context():
        yield app


def configure_test_db(app):
    """Set transient sqlite test db distinguished from dev"""
    db_path = path.dirname(path.abspath(__file__))
    test_db = "sqlite:///" + path.join(db_path, "test.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = test_db


@pytest.fixture(scope="session")
def db(app):

    database.drop_all()
    database.create_all()
    database.session.commit()

    yield database

    database.drop_all()
    database.session.commit()


@pytest.fixture(scope="function")
def client(app):

    yield app.test_client()
