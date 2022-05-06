from . import celery  # get worker instance
from flask import current_app
from .scraper import Job


@celery.task(name="process_file")
def process_job(filename, term_list, page_list):
    job = Job(filename, term_list, page_list)
    print("received!")
    job.process_file()
    return True
