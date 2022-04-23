from src.scraper import Scraper
from flask import Flask, render_template, request
import json
import uuid
import os

app = Flask(__name__)
uploads_dir = os.path.join(app.root_path, "uploads")
output_dir = os.path.join(app.root_path, "output")


@app.route("/")
def get_home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def process_upload():
    name = request.form["name"]
    email = request.form["email"]
    term_list = request.form["term_list"]
    page_list = request.form["page_list"]
    file = request.files["fileupload"]
    file_path = os.path.join(uploads_dir, file.filename)
    output_path = os.path.join(output_dir, "output_csv_" + str(uuid.uuid1()) + ".csv")

    file.save(os.path.join(uploads_dir, file.filename))
    s = Scraper(False, output_path, file_path, term_list, page_list)
    s.processFile()
    return render_template("done.html")


# s = Scraper(True)
# s.setPathToCSV()
# s.processFile()
