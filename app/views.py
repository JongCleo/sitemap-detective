from flask import (
    render_template,
    request,
    current_app,
    Blueprint,
    abort,
    jsonify,
    redirect,
    url_for,
)
from .tasks import process_job, send_email, EmailType
from .models import Job, User, JobSchema, get_or_create
from http import HTTPStatus
from app import db
from celery import chain

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

    ### Write Job to DB
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

    ### Email User Status Page
    status_page_link = url_for("main.get_home") + f"/jobs/{job.id}"
    send_email(EmailType.received, user.email, status_page_link)

    ### Process File
    task_chain = chain(
        process_job.s(job.id), send_email.s(user.email, status_page_link)
    )()

    job.celery_id = task_chain.id
    db.session.add(job)
    db.session.commit()

    # return 303, indicate POST acknowledgement
    # Source: https://stackoverflow.com/questions/4584728/redirecting-with-a-201-created
    return redirect(url_for("main.get_home", job_id=job.id)), HTTPStatus.SEE_OTHER


@main_blueprint.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    # Source: https://stackoverflow.com/questions/9034091/how-to-check-task-status-in-celery
    try:
        job = Job.query.get(job_id)
        status = process_job.AsyncResult(job.celery_id).status
    except Exception as error:
        current_app.logger.info(error)
        abort(HTTPStatus.BAD_REQUEST, "job doesn't exist")

    # Build response object
    job_information = JobSchema().dump(job)
    job_information.update({"status": status})
    job_information.update(
        {
            "output_file_name": job.output_file.filename,
            "input_file_name": job.input_file.filename,
        }
    )

    return (
        render_template("status.html", job_information=job_information),
        HTTPStatus.CREATED,
    )
