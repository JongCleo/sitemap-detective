from http import HTTPStatus
from tests import helpers
import json

# Based on: https://github.dev/paulgoetze/flask-gcs-upload-example-app/blob/part-2/my_app/app.py


def test_valid_job(client, db):
    """
    GIVEN a valid form submission
    WHEN form is submitted to the upload route
    THEN return success confirmation and JSON serialized Job
    """

    # Arrange
    data = {
        "file_upload": helpers.load_file_data("small_test.csv"),
        "email": "test@test.com",
        "term_list": ["connect", "integration"],
        "page_list": ["connect", "integration"],
        "case_sensitive": False,
        "exact_page": False,
    }

    response = client.post(
        "/upload",
        data=data,
        content_type="multipart/form-data",
    )

    data = response.json

    assert response.status_code == HTTPStatus.CREATED  # happy path response
    assert data["celery_id"]  # job was created in celery
    assert data["input_file"]  # file in object storage

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
