# Notes: 
# - we create a non-root user to override Docker default of running processes as root
#   In the event an attacker breaks out of container, they get root access to the host.
FROM python:3.8.9-slim-buster 

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y --no-install-recommends build-essential libpq-dev \      
  && apt-get install -y gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils \
  # install google-chrome and dependencies  
  #&& wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  #&& apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb \  
  # cleaning up unused files
  && rm -rf /var/lib/apt/lists/*
  #&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false

# create directory for app user
WORKDIR /project

# copy and install the dependencies file to the working directory
COPY ./requirements.txt .
RUN pip3 install --upgrade pip \
  && pip3 install -r requirements.txt  

# copy project
COPY . .

# We don't want to run our application as root if it is not strictly necessary, even in a container.
# Create a user and a group called 'app' to run the processes.
# A system user is sufficient and we do not need a home.
RUN adduser --system --group app \
  # Create Log folder
  && mkdir -p logs \
  && touch logs/celery.log \  
  # Hand everything over to the 'app' user in the 'app' group
  && chown -R app:app /project \
  # this also for requests_html module
  && chown -R app:app /home/app \
  && chmod +x start_worker.sh
  
# Subsequent commands, either in this Dockerfile or in a
# docker-compose.yml, will run as user 'app'
USER app

# Force Pyppeteer to download its preferred version of chromium
# No luck with debian release of chromium and regular chrome
#RUN python3 utilities.py download_chromium