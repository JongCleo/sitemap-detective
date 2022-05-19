from flask import (
    render_template,
    request,
    current_app,
    Blueprint,
    abort,
    jsonify,
)
from .tasks import process_job
from .models import Job, User, JobSchema, get_or_create
from http import HTTPStatus
from app import db
from celery.result import AsyncResult

ACCEPTED_MIME_TYPES = {"text/csv", "application/csv"}
main_blueprint = Blueprint("main", __name__, template_folder="templates")


@main_blueprint.route("/")
def get_home():
    current_app.logger.info("index page loading")
    return render_template("index.html")  # why is this the path?


@main_blueprint.route("/upload", methods=["POST"])
def process_upload():

    ### Parse and Validate
    term_list = [x.strip() for x in request.form["term_list"].split(",")]
    page_list = [x.strip() for x in request.form["page_list"].split(",")]
    case_sensitive = (
        request.form["case_sensitive"]
        if request.form["case_sensitive"] == None
        else False
    )
    exact_page = (
        request.form["exact_page"] if request.form["exact_page"] == None else False
    )
    email = request.form["email"]
    file = request.files.get("file_upload")

    if not file:
        print(f"no file,{file}")
        abort(HTTPStatus.BAD_REQUEST, "no file provided")

    mime_types = set(file.content_type.split(","))
    is_mime_type_allowed = any(mime_types.intersection(ACCEPTED_MIME_TYPES))

    if not is_mime_type_allowed:
        abort(HTTPStatus.BAD_REQUEST, f"allowed mimetypes are {ACCEPTED_MIME_TYPES}")

    ### Write Job to DB, Start Workflow
    user = get_or_create(User, email=email)

    job = Job(
        user_id=user.id,
        input_file=file,
        term_list=term_list,
        page_list=page_list,
        case_sensitive=case_sensitive,
        exact_page=exact_page,
    )
    db.session.add(job)
    db.session.commit()

    task = process_job.delay(job.id)
    job.celery_id = task.id
    db.session.commit()

    serializable_job = JobSchema().dump(job)  # python class to python dictionary
    return jsonify(serializable_job), HTTPStatus.CREATED


# @main_blueprint.route("jobs/<id>", methods=["GET"])
# def get_job():
# Source: https://stackoverflow.com/questions/9034091/how-to-check-task-status-in-celery
# job = Job.query.filter_by(id=id)
# res = AsyncResult(job.celery_id)
# first_or_404()
# parse, give back jsonified dump
# pass


# def send_email():
#     #define email properties: sender, recipient, content, and attachment
#     message = Mail(
#     from_email="placeholder",
#     to_emails="TO_EMAIL",
#     subject=f'File',
#     html_content="""
#     <strong>
#     Average price is {}.
#     Minimum price is {}.
#     Maximum price is {}.
#     Std is {}.
#     </strong>
#     """.format(mean_price, min_price, max_price, std_price))
#     attachment = Attachment()
#     attachment.file_content = FileContent(encoded)
#     attachment.file_type = FileType('text/csv')
#     attachment.file_name = FileName('scraped.csv')
#     attachment.disposition = Disposition('attachment')
#     attachment.content_id = ContentId('Example Content ID')
#     message.attachment = attachment

#     #sending out the email
#     try:
#       sg = SendGridAPIClient(SENDGRID_API_KEY)
#       response = sg.send(message)
#       print(response.status_code)
#       print(response.body)
#       print(response.headers)

#     except Exception as e:
#       print(e)
