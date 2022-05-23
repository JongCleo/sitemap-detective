from . import celery  # get worker instance
from flask import current_app
from .scraper import process_job as internal_process_job
import sendgrid
from sendgrid.helpers.mail import *


@celery.task(name="process_file")
def process_job(job_id):
    print("received task, creating job")
    internal_process_job(job_id)
    return


@celery.task(name="confirmation_email")
def confirmation_email(email, job_id):
    print(
        f"making sure sendgrid key is accessible from current app: {current_app.config['SENDGRID_API_KEY']}"
    )
    # TODO: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/transactional_templates.md
    # Use transactional templates for dynamcisim
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config["SENDGRID_API_KEY"])
    from_email = Email("leonardkim96@gmail.com")
    to_email = To(email)
    subject = f"Your File is Being Processed: {job_id}"
    content = Content("text/plain", "here is the link to your status page")
    mail = Mail(from_email, to_email, subject, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


@celery.task(name="done_email")
def done_email(email, job_id):
    pass
