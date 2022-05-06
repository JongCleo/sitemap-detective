#!/bin/bash
# Kill flask server
ps auxww | grep 'flask' | awk '{print $2}' | xargs kill -9

# Kill celery workers
ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9