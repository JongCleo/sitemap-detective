from . import celery  # get worker instance
from flask import current_app
from .scraper import Job


@celery.task(name="process_file")
def process_job(job_id):
    job = Job(job_id)
    print("received!")
    job.process_file()
    return True
