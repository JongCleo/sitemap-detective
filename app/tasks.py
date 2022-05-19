from . import celery  # get worker instance
from flask import current_app
from .scraper import process_job as internal_process_job


@celery.task(name="process_file")
def process_job(job_id):
    print("received task, creating job")
    internal_process_job(job_id)
    return True
