#!/bin/bash
export FLASK_ENV=development

brew services start redis &
flask run &
watchmedo auto-restart -d ./ -p '*.py' -- celery -A celery_worker.celery worker --loglevel=info &
watchmedo auto-restart -d ./ -p '*.py' -- celery --app celery_worker.celery flower --port=5555 &
/usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5555' &
/usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5000'


