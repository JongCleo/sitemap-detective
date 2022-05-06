
# Notes: 
# - we create a non-root user to override Docker default of running processes as root
#   In the event an attacker breaks out of container, they get root access to the host.

FROM python:3.8.3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# We don't want to run our application as root if it is not strictly necessary, even in a container.
# Create a user and a group called 'app' to run the processes.
# A system user is sufficient and we do not need a home.
RUN adduser --system --group --no-create-home app

# create directory for app user
WORKDIR /project

# copy and install the dependencies file to the working directory
RUN pip3 install --upgrade pip
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# copy project
COPY . /project

# Hand everything over to the 'app' user
RUN chown -R app:app /project

# Subsequent commands, either in this Dockerfile or in a
# docker-compose.yml, will run as user 'app'
USER app

# We are done with setting up the image.
# As this image is used for different
# purposes and processes no CMD or ENTRYPOINT is specified here,
# this is done in docker-compose.yml.
