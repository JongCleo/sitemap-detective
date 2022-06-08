from flask import (
    render_template,
    request,
    current_app,
    Blueprint,
    redirect,
    url_for,
    Response,
)
from .tasks import process_job, send_email, EmailType
from .models import Job, User, JobSchema, get_or_create
from http import HTTPStatus
from app import db
from celery import chain
from depot.manager import DepotManager
from sqlalchemy import exc
from wtforms import (
    BooleanField,
    StringField,
    EmailField,
    validators,
    ValidationError,
    SubmitField,
)
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileSize, FileAllowed

ACCEPTED_MIME_TYPES = {"text/csv", "application/csv"}
MAX_FILE_SIZE = 512000
# 1 column * 10k observations
# * 11 utf-8 chars per average domain * 2 bytes per char + 4 * 10k buffer * 2 just bc 250 kb sounded small
main_blueprint = Blueprint("main", __name__, template_folder="templates")


class UploadForm(FlaskForm):
    name = StringField("Name")
    email = EmailField("Email Address", validators=[validators.data_required()])
    term_list = StringField("Terms/Phrases to Search")
    case_sensitive = BooleanField("Case Sensitivity")
    page_list = StringField("Subpages to Search")
    exact_page = BooleanField("Exact Phrasing")
    file_upload = FileField(
        "CSV Upload",
        [
            FileRequired(),
            FileSize(MAX_FILE_SIZE, message="File cannot exceed 250kb"),
            FileAllowed(["csv"], "CSVs only"),
        ],
    )

    submit = SubmitField("Start Job")


@main_blueprint.route("/")
def get_home():
    form = UploadForm(meta={"csrf": False})
    return render_template("index.html", form=form), HTTPStatus.OK


@main_blueprint.route("/upload", methods=["POST"])
def process_upload():
    current_app.logger.info("Handling Upload")
    print(request.form.get("term_list"))
    form = UploadForm(
        data={
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "term_list": request.form.get("term_list"),
            "case_sensitive": request.form.get("case_sensitive"),
            "page_list": request.form.get("page_list"),
            "exact_page": request.form.get("exact_page"),
            "file_upload": request.files.get("file_upload"),
        },
        meta={"csrf": False},
    )

    if not form.validate_on_submit():
        return (
            render_template("index.html", form=form),
            HTTPStatus.BAD_REQUEST,
        )

    ### Write Job to DB
    user = get_or_create(User, email=form.email.data)
    current_app.logger.info(f"Received Upload from User: {user.id}")

    try:
        current_app.logger.info(f"Writing Job to DB")
        job = Job(
            user_id=user.id,
            input_file=form.file_upload.data,
            term_list=[x.strip() for x in form.term_list.data.split(",")],
            page_list=[x.strip() for x in form.page_list.data.split(",")],
            case_sensitive=form.case_sensitive.data,
            exact_page=form.exact_page.data,
        )
        db.session.add(job)
        db.session.commit()
    except exc.SQLAlchemyError as e:
        current_app.logger.error(f"{type(e)} occurred", exc_info=True)
        db.session.rollback()
        return render_template("500.html"), HTTPStatus.INTERNAL_SERVER_ERROR

    ### Email User Status Page
    status_page_link = request.url_root + f"jobs/{job.id}"
    current_app.logger.debug(status_page_link)

    send_email.delay(EmailType.received, user.email, status_page_link)

    ### Process File
    task_chain = chain(
        process_job.s(job.id), send_email.s(user.email, status_page_link)
    )()

    job.celery_id = task_chain.id
    db.session.add(job)
    db.session.commit()

    # 303 == POST acknowledgement, Src: https://stackoverflow.com/questions/4584728/redirecting-with-a-201-created
    return redirect(url_for("main.get_job", job_id=job.id)), HTTPStatus.SEE_OTHER


@main_blueprint.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    current_app.logger.info(f"Status page loading, job id: {job_id}")
    # Source: https://stackoverflow.com/questions/9034091/how-to-check-task-status-in-celery
    try:
        job = Job.query.get(job_id)
        status = process_job.AsyncResult(job.celery_id).status
    except Exception as error:
        current_app.logger.info(f"Job ID: {job_id} does not exist")
        return render_template("404.html"), HTTPStatus.NOT_FOUND

    # Build response object
    job_information = JobSchema().dump(job)

    job_information.update(
        {
            "created_at": job.created_at,
            "status": status,
            "output_file_name": "N/A"
            if job.output_file is None
            else job.output_file.filename,  # flattening bc Jinja can't parse nested props
            "input_file_name": job.input_file.filename,
            "page_list": job.page_list,  # use string form
            "term_list": job.term_list,
        }
    )

    return (
        render_template("status.html", job_information=job_information),
        HTTPStatus.CREATED,
    )


@main_blueprint.route("/downloads/<job_id>", methods=["GET", "POST"])
def download_output_file(job_id):
    current_app.logger.info(f"Download requested for job id: {job_id}")
    output_file_path = Job.query.get(job_id).output_file.path
    output_file = DepotManager.get_file(output_file_path)

    # not expecting big files.. should be fine to read into memory and hail mary w.o chunking
    return Response(
        output_file.read(),
        mimetype="text/csv",
        headers={f"Content-Disposition": "attachment;filename=" + output_file.filename},
    )
