#!/bin/bash

python3 utilities.py download_chromium 
celery -A celery_worker.celery worker --loglevel=info --logfile=logs/celery.log