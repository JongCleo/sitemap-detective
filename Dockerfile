# Notes: 
# - we create a non-root user to override Docker default of running processes as root
#   In the event an attacker breaks out of container, they get root access to the host.

FROM python:3.8.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \        
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*    

# We don't want to run our application as root if it is not strictly necessary, even in a container.
# Create a user and a group called 'app' to run the processes.
# A system user is sufficient and we do not need a home.
RUN adduser --system --group app

# create directory for app user
WORKDIR /project

# copy and install the dependencies file to the working directory
RUN pip3 install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# install google-chrome and dependencies
RUN apt-get update \
  && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && apt-get install -y ./google-chrome-stable_current_amd64.deb \  
  && rm -rf /var/lib/apt/lists/*  

# Create Log folder
RUN mkdir -p logs
RUN touch logs/celery.log

# copy project
COPY . /project 

# Hand everything over to the 'app' user in the 'app' group
RUN chown -R app:app /project
# this also for requests_html module
RUN chown -R app:app /home/app

# Subsequent commands, either in this Dockerfile or in a
# docker-compose.yml, will run as user 'app'
USER app

# Force Pyppeteer to download its preferred version of chromium
# No luck with debian release of chromium and regular chrome
RUN python3 utilities.py download_chromium

# We are done with setting up the image.
# As this image is used for different
# purposes and processes no CMD or ENTRYPOINT is specified here,
# this is done in docker-compose.yml.
