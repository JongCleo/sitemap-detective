import os
from requests_html import HTMLSession


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["csv"]


def is_valid_url(url: str) -> bool:
    """makes a test request against URL to see if it exists (returns a 200)

    Args:
        url (str): url to be tested

    Returns:
        bool: returns true if the request was successful
    """

    with HTMLSession() as session:
        try:
            r = session.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                return True
            else:  # valid domain but failed request TODO: notion of retries
                return False
        except:  # invalid domain, connection error
            return False


def clean_output_directory():
    path_to_output = get_output_directory()
    output_files = os.listdir(path_to_output)

    if len(output_files) >= 1:
        for filename in output_files:
            file_path = os.path.join(path_to_output, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))


def get_upload_directory():
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_uploads = os.path.join(cwd, "./uploads")
    return path_to_uploads


def get_output_directory():
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_output = os.path.join(cwd, "./output")
    return path_to_output
