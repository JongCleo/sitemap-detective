import os
from requests_html import HTMLSession

def __is_valid_url(url: str):
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
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_output = os.path.join(cwd, "../output")
    output_files = os.listdir(path_to_output)

    if len(output_files) >= 1:
        for filename in output_files:
            file_path = os.path.join(path_to_output, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))
