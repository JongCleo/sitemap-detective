from custom_requests_html.requests_html import HTMLSession
import chardet
import csv
import subprocess


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


def guess_encoding(encoded_bytes):
    result = chardet.detect(encoded_bytes)
    return result.get("encoding")


def guess_csv_dialect(csv_string):
    return csv.Sniffer().sniff(csv_string)


# Internal method returns Type String "path" to chromium executable
# Returns Bool false if no executable is found
def _get_chromium_executable_path():
    search_process = subprocess.Popen(
        "whereis chromium",
        shell=True,
        stdout=subprocess.PIPE,
    )
    executable_paths = search_process.communicate()[0].decode("utf-8").split(" ")
    executable_exists = len(executable_paths) > 1
    if executable_exists:
        exec_path = executable_paths.split(" ")[1]
        # expected output is "chromium: pathA pathB ...."
        return exec_path
    return False


# Method return tuple containing List<str> for browser args
# and Dict for pyppeteer args req'd in HTMLSession constructor
# need this special configuration is because docker is a finicky POS
def get_chromium_configuration():
    browser_args = ["--headless", "--no-sandbox", "--disable-dev-shm-usage"]
    pyppeteer_args = {}
    if executable_path := _get_chromium_executable_path():
        pyppeteer_args["executablePath"] = executable_path
    return (browser_args, pyppeteer_args)
