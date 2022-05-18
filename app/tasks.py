from . import celery  # get worker instance
from flask import current_app
from .scraper import Job


@celery.task(name="process_file")
def process_job(job_id):
    print("received task, creating job")
    job = Job(job_id)
    # job.process_file()
    return True
