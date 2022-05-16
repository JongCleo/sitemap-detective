from http import HTTPStatus
from tests import helpers


def test_file_upload(client):
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


# user submits a file, job is created, file gets stored

# file is too big, file wrong format
# rate limiting case
# new user signs up, user is created
