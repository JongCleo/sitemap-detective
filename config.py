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

    ## Object Store
    GOOGLE_CLOUD_STORAGE_ACCESS_KEY = os.getenv("GOOGLE_CLOUD_STORAGE_ACCESS_KEY")
    GOOGLE_CLOUD_STORAGE_SECRET_KEY = os.getenv("GOOGLE_CLOUD_STORAGE_SECRET_KEY")
    GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    ## Dababase
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ## Email
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
    SENDGRID_TEMPLATE_ID = os.getenv("SENDGRID_TEMPLATE_ID")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base_dir, "database.db")
    DEPOT_CONFIG = {"depot.storage_path": "./tmp/"}


class ProductionConfig(Config):
    DEBUG = False
    DEPOT_CONFIG = {
        "depot.backend": "depot.io.boto3.S3Storage",
        "depot.endpoint_url": "https://storage.googleapis.com",
        "depot.access_key_id": os.getenv("GOOGLE_CLOUD_STORAGE_ACCESS_KEY"),
        "depot.secret_access_key": os.getenv("GOOGLE_CLOUD_STORAGE_SECRET_KEY"),
        "depot.bucket": os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET"),
    }
