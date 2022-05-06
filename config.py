import os
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class, contains default settings,"""

    DEBUG = False
    TESTING = False
    FLASK_ENV = os.getenv("FLASK_ENV")

    # Secrets for all environments
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    RESULT_BACKEND = os.getenv("RESULT_BACKEND")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass
