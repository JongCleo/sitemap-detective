from . import celery  # get worker instance
from flask import current_app
from .scraper import Job


@celery.task(name="process_file")
def process_job():
    print("received!")
    # job.process_file()
    return True
