from requests_html import HTMLSession
import chardet
import csv
import sys
import os
import logging


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


class HiddenPrints:
    """context provider to prevent the Ultimate Sitemap Parser library from spamming stdout"""

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        logging.disable(logging.CRITICAL)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        logging.disable(logging.NOTSET)
