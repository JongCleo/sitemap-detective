from . import celery  # get worker instance
from flask import current_app
from .scraper import process_job as internal_process_job
import sendgrid
from sendgrid.helpers.mail import *
import enum

# Want to subclass string so it's celery compatible
# Source: https://stackoverflow.com/questions/24481852/serialising-an-enum-member-to-json
class EmailType(str, enum.Enum):
    received = "received"
    succeeded = "succeeded"
    failed = "failed"


@celery.task(name="process_file")
def process_job(job_id):
    current_app.logger.info("Processing File...")
    try:
        internal_process_job(job_id)
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
