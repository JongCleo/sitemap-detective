import os
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class, contains default settings,"""

    DEBUG = False
    TESTING = False
    FLASK_ENV = os.getenv("FLASK_ENV")

    # Celery Workers
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    RESULT_BACKEND = os.getenv("RESULT_BACKEND")

    ## Object STore
    GOOGLE_CLOUD_STORAGE_ACCESS_KEY = os.getenv("GOOGLE_CLOUD_STORAGE_ACCESS_KEY")
    GOOGLE_CLOUD_STORAGE_SECRET_KEY = os.getenv("GOOGLE_CLOUD_STORAGE_SECRET_KEY")
    GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    ## Dababase
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass
