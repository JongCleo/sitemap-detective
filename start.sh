#!/bin/bash

# Convenient script for setting up Dev environment
# Clean up lingering processes
./stop.sh

# export ENV variables
export $(grep -v '^#' dev.env | xargs)

# Clean celery cache
celery -A celery_worker.celery purge -f

# Create a local SQLliteDB from scratch
python ./utilities.py create_db

# Create log artifacts if DNE
mkdir -p logs
touch logs/celery.log

# start app, worker and worker dashboard
docker-compose -f docker-compose-dev.yml up -d

# overwrite the celery ENV vars so Flask Container can talk to Redis Container
# and celery/flower runnning on the Host machine can talk to Redis Container
export REDIS_URL=redis://localhost:6379
watchmedo auto-restart -d 'app/' -p '*.py' -- celery -A celery_worker.celery worker --loglevel=info &
watchmedo auto-restart -d 'app/' -p '*.py' -- celery --app celery_worker.celery flower --port=5555 &

# open browsers
#/usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5555/' &
#usr/bin/open -a "/Applications/Google Chrome.app" 'http://localhost:5000/'


