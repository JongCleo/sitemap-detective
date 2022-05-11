#!/bin/bash

# Kill active stuff
ps auxww | grep -E 'divisional' | awk '{print $2}' | xargs kill -9

#ps auxww | grep 'divisional' 