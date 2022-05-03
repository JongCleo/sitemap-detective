#set base image
FROM python:3

# set the working directory in the container
WORKDIR /code

# copy and install the dependencies file to the working directory
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

COPY ./ ./
CMD [ "python", "./src/scraper.py" ]