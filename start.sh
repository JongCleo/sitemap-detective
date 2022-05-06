#!/bin/bash
brew services start redis &
flask run &
celery -A celery_worker.celery worker --loglevel=info &
celery --app celery_worker.celery flower --port=5555 --broker=redis://redis:6379/0

# PY_PATH = "${PWD}/venv/bin/python"
# CELERY_PATH = "${PWD}/venv/bin/python"
# osascript -e 'tell app "Terminal" to do script "${PY_PATH} application.py"'
# osascript -e 'tell app "Terminal" to do script "celery -A celery_worker.celery worker --loglevel=info"'



