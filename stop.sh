#!/bin/bash

# Kill active stuff
ps auxww | grep -E 'celery worker|celery flower|flask' | awk '{print $2}' | xargs kill -9
