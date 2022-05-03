import os
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class, contains default settings,"""

    FLASK_ENV = "development"
    DEBUG = False
    TESTING = False

    # Secrets for all environments
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass
