"""
This contains the application factory for creating flask application instances.
Using the application factory allows for the creation of flask applications configured 
for different environments based on the value of the CONFIG_TYPE environment variable
Based on https://github.com/angeuwase/production-flask-app-setup
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from config import Config
from flask.logging import default_handler
from depot.manager import DepotManager

### Instantiate Celery
celery = Celery(
    __name__,
    broker=Config.CELERY_BROKER_URL,
    backend=Config.RESULT_BACKEND,
    # task_ignore_result=True,
)

### Instantiate db
db = SQLAlchemy()

### Application Factory
def create_app():

    app = Flask(__name__)

    # Configure the flask app instance
    CONFIG_TYPE = os.getenv("CONFIG_TYPE", default="config.DevelopmentConfig")
    app.config.from_object(CONFIG_TYPE)

    # Configure celery
    celery.conf.update(app.config)
    # Subclass of task that wraps the task execution in application context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # Configure database
    register_database(app)

    # Register blueprints
    register_blueprints(app)

    # Configure logging
    configure_logging(app)

    # Register error handlers
    register_error_handlers(app)

    # Setup File storage
    setup_depots(app)

    return app


### Helper Functions ###
def register_blueprints(app):
    from app import views

    app.register_blueprint(views.main_blueprint)


def register_error_handlers(app):

    # 400 - Bad Request
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("400.html"), 400

    # 403 - Forbidden
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    # 404 - Page Not Found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # 405 - Method Not Allowed
    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template("405.html"), 405

    # 500 - Internal Server Error
    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500


def configure_logging(app):

    # Deactivate the default flask logger so that log messages don't get duplicated
    app.logger.removeHandler(default_handler)

    # Create a file handler object
    file_handler = RotatingFileHandler(
        "logs/flaskapp.log", maxBytes=16384, backupCount=20
    )

    # Set the logging level of the file handler object so that it logs INFO and up
    file_handler.setLevel(logging.INFO)

    # Create a file formatter object
    file_formatter = logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]"
    )

    # Apply the file formatter object to the file handler object
    file_handler.setFormatter(file_formatter)

    # Add file handler object to the logger
    app.logger.addHandler(file_handler)


def register_database(app):
    from app import models

    with app.app_context():
        db.init_app(app)


def setup_depots(app):

    depot_name = "all_csvs"
    # storing on disk vs memory per https://github.com/amol-/depot/tree/master/examples/flask
    depot_config = app.config.get("DEPOT_CONFIG")

    DepotManager.configure(depot_name, depot_config)
    # MWare to serve files
    app.wsgi_app = DepotManager.make_middleware(app.wsgi_app)
