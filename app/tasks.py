from . import celery  # get worker instance
from flask import current_app
from .scraper import process_job as internal_process_job
import sendgrid
from sendgrid.helpers.mail import *
import enum


@celery.task(name="process_file")
def process_job(job_id):
    print("received task, creating job")
    internal_process_job(job_id)
    return EmailType.succeeded


class EmailType(enum.Enum):
    received = 1
    succeeded = 2
    failed = 3


@celery.task(name="send_email")
def send_email(email_type: EmailType, email: str, status_page_link: str):

    print(
        f"making sure sendgrid key is accessible from current app: {current_app.config['SENDGRID_API_KEY']}"
    )

    # TODO: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/transactional_templates.md
    # Use transactional templates for dynamcisim
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config["SENDGRID_API_KEY"])
    from_email = Email("leonardkim96@gmail.com")
    to_email = To(email)

    if email_type == EmailType.received:
        subject = "Your File is Being Processed"
        content = Content("text/plain", "here is the link to your status page")
    elif email_type == EmailType.succeeded:
        subject = "Your File is Ready"
        content = Content(
            "text/plain", "here is the link where you can download your lead list!"
        )
    else:
        pass

    mail = Mail(
        from_email, to_email, subject, content, status_page_link=status_page_link
    )

    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
