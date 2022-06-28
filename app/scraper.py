import os
import re
import csv
import uuid
import requests
from urllib.parse import urlparse
from requests_html import HTMLSession
from flask import current_app
import io

from custom_usp.tree import sitemap_tree_for_homepage
from app import db
from . import celery  # get worker instance
from .helper_functions import *
from .models import Job


def get_urls(input_file) -> list:
    """Parses the file-to-be-processed into a list of urls
    Args:
        input_file: StoredFile object from depot pckg which extends IOBase
    """

    input_urls = []
    input_file_bytes = input_file.read()
    deduced_encoding = guess_encoding(input_file_bytes)

    file_str = input_file_bytes.decode(deduced_encoding)
    file_io = io.StringIO(file_str)
    reader = csv.reader(file_io)
    for line in reader:
        domain = line[0]
        if not re.match("(?:http|ftp|https)://", domain):
            input_urls.append("http://{}".format(domain))
        else:
            input_urls.append(domain)
    input_file.close()

    return input_urls


@celery.task(name="process_url")
def process_url(
    input_url: str,
    term_list: list,
    page_list: list,
    case_sensitive: bool,
    exact_page: bool,
) -> str:
    """Searches URL for specified keywords on-page and in its sitemap

    Returns:
        str: comma separated row of boolean values indicating whether search terms
        and pages were found for the given input_url. The order corresponds to the headers in __make_output_file()
    """
    if not is_valid_url(input_url):
        res = ",".join(
            [input_url]
            + ["N/A" for i in range(len(term_list))]
            + ["N/A" for i in range(len(page_list))]
        )
        return res

    term_exist_list = find_terms_on_homepage(input_url, term_list, case_sensitive)
    page_exist_dict = find_pages_in_sitemap(input_url, page_list, exact_page)

    res = ",".join([input_url] + term_exist_list + list(page_exist_dict.values()))

    return res


def find_terms_on_homepage(site: str, term_list: list, case_sensitive: bool) -> list:
    """Searches homepage of site for specified keywords

    Returns:
        list: list of boolean terms indicating presence of each keyword,
        corresponding to the header in __make_output_file()
    """
    current_app.logger.info("Searching homepage for keywords...")
    term_exist_list = []

    with HTMLSession(
        browser_args=[
            "--headless",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--single-process",
        ]
    ) as session:
        try:
            r = session.get(site, headers={"User-Agent": "Mozilla/5.0"})
        except requests.exceptions.RequestException as e:
            current_app.logger.warning(f"Failed to fetch homepage error {e}")
            for term in term_list:
                term_exist_list.append("N/A")
            return term_exist_list
        try:
            r.html.render(timeout=25)
            for term in term_list:
                if term in r.html.html:
                    term_exist_list.append("True")
                else:
                    term_exist_list.append("False")
        except Exception as e:
            current_app.logger.warning(f"Render likely timed out. {e}")
            for term in term_list:
                term_exist_list.append("N/A")

    return term_exist_list


def find_pages_in_sitemap(site: str, page_list: list, exact_page: bool) -> dict:
    """Searches sitemap(s) of site for specified subpages

    Args:
        site (str): url of site to be searched

    Returns:
        dict: dict of boolean terms indicating presence of each subpage,
        corresponding to the header in __make_output_file()
    """
    page_exist_dict = {pg: "False" for pg in page_list}
    with HiddenPrints():
        try:
            tree = sitemap_tree_for_homepage(site)
        except Exception as e:
            current_app.logger.error(f"Failed to fetch sitemap {e}")
            return page_exist_dict

    current_app.logger.info("Searching sitemap...")
    for page in tree.all_pages():
        potential_match = urlparse(page.url).path

        if (
            len(potential_match) <= 1
        ):  # Catch dumb edge case for invisible strings which throw outOfBounds errors in the logic below
            continue

        potential_match = (
            potential_match[1:] if potential_match[0] == "/" else potential_match
        )

        for search_term in page_exist_dict:
            if (exact_page and search_term == potential_match) or (
                not exact_page and search_term in potential_match
            ):
                page_exist_dict[search_term] = "True"

    return page_exist_dict


@celery.task(name="finish_job", bind=True, max_retries=3)
def finish_job(self, db_job: Job, input_filename: str, headers, result_list) -> None:
    # Parse pickled objects
    headers = list(headers)
    result_list = [result.split(",") for result in list(result_list)]

    temp_file = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        f"{input_filename.rsplit('.',1)[0]}_{uuid.uuid4().hex}.csv",
    )
    with open(temp_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(result_list)
    try:
        with open(temp_file, "rb") as f:
            db_job.output_file = f
            db.session.commit()
    except Exception as exc:
        current_app.logger.error(f"Failed to write to db {exc}")
        self.retry(countdown=10, exc=exc)

    try:
        os.remove(temp_file)
    except OSError:
        pass
