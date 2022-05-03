from . import main_blueprint
from flask import render_template, request, redirect, url_for, current_app
import os
import uuid
from ..helper_functions import allowed_file, get_output_directory, get_upload_directory
from ..tasks import process_job


# os.makedirs(uploads_dir, exists_ok=True)
# os.makedirs(output_dir, exists_ok=True)


@main_blueprint.route("/")
def get_home():
    current_app.logger.info("index page loading")
    return render_template("main/index.html")  # why is this the path?


@main_blueprint.route("/upload", methods=["POST"])
def process_upload():
    process_job.delay()
    # email = request.form["email"]
    # term_list = request.form["term_list"]
    # page_list = request.form["page_list"]
    # file = request.files["fileupload"]

    # # check if the post request has the file part
    # if "file" not in request.files:
    #     return "No file part"
    # if file.filename == "":
    #     return "No selected file"
    # if file and allowed_file(file.filename):
    #     file_path = os.path.join(get_upload_directory(), file.filename)
    # output_path = os.path.join(
    #     get_output_directory(), "output_csv_" + str(uuid.uuid1()) + ".csv"
    # )

    # Connect to db
    # write file to bucket
    # save Job to db

    # file.save(os.path.join(get_upload_directory(), file.filename))
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
