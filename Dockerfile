#set base image
FROM python:3

# set the working directory in the container
WORKDIR /code

# copy and install the dependencies file to the working directory
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./ ./
CMD [ "python", "./src/scraper.py" ]