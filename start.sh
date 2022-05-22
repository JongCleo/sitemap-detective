#!/bin/bash

# clean up and setup
./stop.sh
celery -A celery_worker.celery purge -f
python ./utilities.py create_db
brew services start redis

# start app, worker and worker dashboard
flask run &
watchmedo auto-restart -d 'app/' -p '*.py' -- celery -A celery_worker.celery worker --loglevel=info &
watchmedo auto-restart -d 'app/' -p '*.py' -- celery --app celery_worker.celery flower --port=5555

# open browsers
#/usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5555/' &
#usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5000/'


