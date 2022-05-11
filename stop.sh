#!/bin/bash

# Kill active stuff
ps auxww | grep -E 'celery worker|celery flower|flask|watchemedo' | awk '{print $2}' | xargs kill -9
