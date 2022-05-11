from flask import render_template, request, redirect, url_for, current_app, Blueprint
import os
import uuid
from .helper_functions import allowed_file, get_output_directory, get_upload_directory
from .tasks import process_job
from .models import User, Job


ACCEPTED_MIME_TYPES = {"text/csv", "application/csv"}
main_blueprint = Blueprint("main", __name__, template_folder="templates")

# os.makedirs(uploads_dir, exists_ok=True)
# os.makedirs(output_dir, exists_ok=True)


@main_blueprint.route("/")
def get_home():
    current_app.logger.info("index page loading")
    return render_template("index.html")  # why is this the path?


@main_blueprint.route("/upload", methods=["POST"])
def process_upload():
    # job = create or update Job in database

    # Parse and Validate Request
    term_list = request.form["term_list"]
    page_list = request.form["page_list"]
    email = request.form["email"]
    file = request.files.get("file_upload")

    if not file:
        pass
        # abort(HTTPStatus.BAD_REQUEST, 'no image file provided')

    mime_types = set(file.content_type.split(","))
    is_mime_type_allowed = any(mime_types.intersection(ACCEPTED_MIME_TYPES))

    if not is_mime_type_allowed:
        pass
        # abort(HTTPStatus.BAD_REQUEST, f'allowed mimetypes are {IMAGE_MIME_TYPES}')

    # Store File

    # Add Job
    process_job.delay(file.filename, term_list, page_list)

    # if file and allowed_file(file.filename):
    #     file_path = os.path.join(get_upload_directory(), file.filename)
    # output_path = os.path.join(
    #     get_output_directory(), "output_csv_" + str(uuid.uuid1()) + ".csv"
    # )

    return "nice"


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
