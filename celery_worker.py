#!/usr/bin/env python
# See: https://github.com/angeuwase/production-flask-app-setup/blob/main/celery_worker.py
from app import create_app

app = create_app()
with app.app_context():
    # need create_app() to run before importing celery so the
    # celery instance is configured properly

    from app import celery
