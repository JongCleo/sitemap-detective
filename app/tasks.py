from celery import group
from celery.result import allow_join_result
from depot.manager import DepotManager
from flask import current_app
import enum
import sendgrid
from sendgrid.helpers.mail import *
import time

from .scraper import *
from . import celery  # get worker instance


# Want to subclass string so it's celery compatible
# Source: https://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
class EmailType(str, enum.Enum):
    received = "received"
    succeeded = "succeeded"
    failed = "failed"


# This is anti pattern-ish as the core logic should be implemented in its own fncs
# Tasks' main concerns are serialization, message headers, retries..
@celery.task(name="process_job")
def process_job(job_id):
    """Checks a list of domains for the existence of certain pages and keywords in each domains' sitemaps"""
    current_app.logger.info("Processing File...")
    try:
        ### Load data into memory from DB
        current_app.logger.info("Loading job data into memory")
        db_job = Job.query.get(job_id)
        input_file = DepotManager.get_file(db_job.input_file.path)
        input_urls = get_urls(input_file)
        term_list = db_job.term_list
        page_list = db_job.page_list
        case_sensitive = db_job.case_sensitive
        exact_page = db_job.exact_page
        headers = (
            ["sites"]
            + list(map(lambda term: "term_" + term, term_list))
            + list(map(lambda page: "page_" + page, page_list))
        )

        ### Line up subjobs
        current_app.logger.info("Pawning off URLs to Subtasks")
        job_list = [
            process_url.s(url, term_list, page_list, case_sensitive, exact_page)
            for url in input_urls
        ]

        result = group(job_list).apply_async()
        while not result.ready():
            time.sleep(5)
        with allow_join_result():
            result_list = result.get()

        current_app.logger.info("Writing to Output File...")
        finish_job(db_job, input_file.filename, headers, result_list)
    except Exception as e:
        current_app.logger.error(e, exc_info=True)
        return EmailType.failed
    return EmailType.succeeded


@celery.task(name="send_email", bind=True, max_retries=3)
def send_email(self, email_type: EmailType, email: str, status_page_link: str):
    current_app.logger.info("Sending Email...")
    # TODO: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/transactional_templates.md
    # Use transactional templates for dynamcisim

    from_email = Email(current_app.config["SENDGRID_FROM_EMAIL"])
    to_email = To(email)

    if email_type == EmailType.received:
        subject = "Your File is Being Processed"
        html_content = "<strong>Your file is being processed.</strong>"
    elif email_type == EmailType.succeeded:
        subject = "Your File is Ready"
        html_content = "<strong>Your file is ready.</strong>"
    else:
        subject = "Something Went Wrong, We're Investigating"
        html_content = "<strong>We could not process your file. I'm looking into it and I'll send the processed version directly to you so you don't have to resubmit.</strong>"

    mail = Mail(from_email, to_email, subject, html_content)
    mail.dynamic_template_data = {
        "status_page_link": f"{status_page_link}",
    }
    mail.template_id = current_app.config["SENDGRID_TEMPLATE_ID"]

    try:
        sg = sendgrid.SendGridAPIClient(api_key=current_app.config["SENDGRID_API_KEY"])
        sg.client.mail.send.post(request_body=mail.get())
    except Exception as exc:
        current_app.logger.error(exc, exc_info=True)
        self.retry(countdown=10, exc=exc)
        # What to do here TBD, send an email to self?
        # or raise HTTP error back to flask server?
