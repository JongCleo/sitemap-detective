import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class, contains default settings,"""

    DEBUG = False
    TESTING = False
    FLASK_ENV = os.getenv("FLASK_ENV")

    # Celery Workers
    CELERY_BROKER_URL = os.getenv("REDIS_URL")
    RESULT_BACKEND = os.getenv("REDIS_URL")

    ## Object Store
    GOOGLE_CLOUD_STORAGE_ACCESS_KEY = os.getenv("GOOGLE_CLOUD_STORAGE_ACCESS_KEY")
    GOOGLE_CLOUD_STORAGE_SECRET_KEY = os.getenv("GOOGLE_CLOUD_STORAGE_SECRET_KEY")
    GOOGLE_CLOUD_STORAGE_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

    ## Dababase
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    }

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
