from http import HTTPStatus
from tests import helpers

# Based on: https://github.dev/paulgoetze/flask-gcs-upload-example-app/blob/part-2/my_app/app.py


def test_valid_job(client):
    """
    GIVEN a valid form submission
    WHEN form is submitted to the upload route
    Then a success confirmation and jsonified job object is returned to the client
    """

    small_csv = helpers.load_file_data("small_test.csv")

    response = client.post(
        "/upload",
        data={"file_upload": small_csv, "email": "tomato@gmail.com"},
        content_type="multipart/form-data",
    )

    data = response.json
    print(data)
    assert response.status_code == HTTPStatus.CREATED
    # assert file exists in object storage
    # assert that a job was created in celery
    # assert that email was sent


def test_valid_job_finishes():
    """
    Given a valid form submission
    When the worker is done processing the file
    User receives an email to the status page with a valid download link
    """
    pass


def test_job_with_invalid_mime_type():
    """
    Given a file of non-csv
    When submitted to server
    Server throws a BAD_REQUEST
    """
    pass


def test_job_with_invalid_file_format():
    """
    Given a file without a
    When submitted to server
    Server throws a BAD_REQUEST
    """
    # different delimiter types
    # multiple columns, header no header
    # empty file
    # weird encoding
    # too big
    pass


def test_spam_protection():
    pass
    # rate limiting case


def test_create_user():
    pass


def test_create_a_duplicate_user():
    pass
