#!/bin/bash

# clean up and setup
./stop.sh
export $(grep -v '^#' dev.env | xargs)
celery -A celery_worker.celery purge -f
python ./utilities.py create_db
brew services start redis
mkdir -p logs
touch logs/celery.log

# start app, worker and worker dashboard
watchmedo auto-restart -d 'app/' -p '*.py' -- celery -A celery_worker.celery worker --loglevel=info --logfile=logs/celery.log &
watchmedo auto-restart -d 'app/' -p '*.py' -- celery --app celery_worker.celery flower --port=5555 &
flask run -p 5050

# open browsers
#/usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5555/' &
#usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5000/'


