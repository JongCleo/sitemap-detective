#!/bin/bash

# Kill active stuff
docker-compose -f docker-compose-dev.yml down
ps auxww | grep -E 'divisional' | awk '{print $2}' | xargs kill -9

#ps auxww | grep 'divisional' 