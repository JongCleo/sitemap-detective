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
    print("received task, creating job")
    internal_process_job(job_id)
    return EmailType.succeeded


@celery.task(name="send_email")
def send_email(email_type: EmailType, email: str, status_page_link: str):

    # TODO: https://github.com/sendgrid/sendgrid-python/blob/main/use_cases/transactional_templates.md
    # Use transactional templates for dynamcisim
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config["SENDGRID_API_KEY"])
    from_email = Email("leonardkim96@gmail.com")
    to_email = To(email)

    if email_type == EmailType.received:
        subject = "Your File is Being Processed"
    elif email_type == EmailType.succeeded:
        subject = "Your File is Ready"
        # content = Content(
        #     "text/plain", "here is the link where you can download your lead list!"
        # )
    else:
        pass

    mail = Mail(
        from_email,
        to_email,
        subject,
        html_content="<strong>Your file is being processed. Or maybe it's done.</strong>",
    )
    mail.dynamic_template_data = {
        "status_page_link": f"{status_page_link}",
    }
    mail.template_id = "d-e74a9bbeb60047b5b294a3de5ad7c2be"

    try:
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
