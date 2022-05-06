#!/bin/bash
brew services start redis &
flask run &
celery -A celery_worker.celery worker --loglevel=info &
celery --app celery_worker.celery flower --port=5555 --broker=redis://redis:6379/0


