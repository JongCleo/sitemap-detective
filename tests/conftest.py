from os import path
import pytest
from app import create_app, db as database
from app.models import Job, User
from tests import helpers
from flask import template_rendered


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


@pytest.fixture
def user(db):
    user = User(email="test@test.com")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def job(user, db):
    input_file = helpers.load_binary_file("small_test.csv")
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    job = Job(
        user_id=user.id, input_file=input_file, term_list=term_list, page_list=page_list
    )
    db.session.add(job)
    db.session.commit()
    return job


@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
