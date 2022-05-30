from http import HTTPStatus
from tests import helpers

# Based on: https://github.dev/paulgoetze/flask-gcs-upload-example-app/blob/part-2/my_app/app.py


def test_get_homepage(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK


def test_post_valid_upload(client, db, captured_templates):
    """
    GIVEN a form submission
    WHEN the form passes validation checks
    AND is written to the database
    THEN the user is redirected to a status monitoring page
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
        "/upload", data=data, content_type="multipart/form-data", follow_redirects=True
    )

    assert response.status_code == HTTPStatus.CREATED  # happy path response
    assert len(captured_templates) == 1
    template, context = captured_templates[0]

    assert template.name == "status.html"
    assert "celery_id" in str(context)
    assert "input_file_name" in str(context)


def test_invalid_mime_type_upload():
    """
    Given a file of non-csv
    When submitted to server
    Server throws a BAD_REQUEST
    """
    pass


def test_invalid_file_format_upload():
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


def test_get_valid_job():
    pass


def test_get_invalid_job():
    pass


def test_get_valid_download():
    pass


def test_get_invalid_download():
    pass
