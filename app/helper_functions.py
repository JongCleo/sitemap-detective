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
