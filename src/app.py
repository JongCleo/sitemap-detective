from scraper import Job
from flask import Flask, render_template, request, redirect, url_for
import uuid
from helper_functions import allowed_file
import os

app = Flask(__name__)

uploads_dir = os.path.join(app.instance_path, 'uploads')
output_dir = os.path.join(app.instance_path, "output")
os.makedirs(uploads_dir, exists_ok=True)
os.makedirs(output_dir, exists_ok=True)


@app.route("/")
def get_home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def process_upload():
    email = request.form["email"]
    term_list = request.form["term_list"]
    page_list = request.form["page_list"]
    file = request.files["fileupload"]

    # check if the post request has the file part
    if "file" not in request.files:
        return "No file part"        
    if file.filename == "":
        return "No selected file"
    if file and allowed_file(file.filename):
        file_path = os.path.join(uploads_dir, file.filename)
    output_path = os.path.join(output_dir, "output_csv_" + str(uuid.uuid1()) + ".csv")

    # Connect to db
    # write file to bucket
    # save Job to db

    file.save(os.path.join(uploads_dir, file.filename))
    return render_template("done.html")


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