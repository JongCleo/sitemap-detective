from flask.cli import FlaskGroup
from app import create_app, db
import os
import shutil
from custom_requests_html.requests_html import HTMLSession
from app.helper_functions import get_chromium_executable_path

cli = FlaskGroup(create_app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("test_chromium")
def download_chromium():
    browser_args = ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
    pyppeteer_args = {}
    if executable_path := get_chromium_executable_path():
        pyppeteer_args["executablePath"] = executable_path

    with HTMLSession(
        browser_args=browser_args, pyppeteer_args=pyppeteer_args
    ) as session:
        r = session.get("https://google.com", headers={"User-Agent": "Mozilla/5.0"})
        r.html.render(timeout=15)
        print(r.html)


@cli.command("clean_temp_dir")
def clean_temp_directory():
    cwd = os.path.abspath(os.path.dirname(__file__))
    temp_dir = os.path.join(cwd, "tmp/")

    shutil.rmtree(temp_dir)
    # files_to_del = os.listdir(temp_dir)

    # if len(files_to_del) >= 1:
    #     for filename in files_to_del:
    #         file_path = os.path.join(temp_dir, filename)
    #         try:
    #             if os.path.isfile(file_path) or os.path.islink(file_path):
    #                 os.unlink(file_path)
    #         except Exception as e:
    #             print("Failed to delete %s. Reason: %s" % (file_path, e))


if __name__ == "__main__":
    cli()
