import os, sys
import re
import billiard as mp
import csv
import uuid
import requests
from usp.tree import sitemap_tree_for_homepage
import logging
from urllib.parse import urlparse
from requests_html import HTMLSession
from .helper_functions import is_valid_url
from .models import Job
from depot.manager import DepotManager
from app import db


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


def process_job(job_id: str):
    """Checks a list of domains for the existence of certain pages and keywords in each domains' sitemaps"""

    ### Load data into memory from DB
    db_job = Job.query.get(job_id)
    input_file = DepotManager.get_file(db_job.input_file.path)
    input_urls = get_urls(input_file)
    term_list = db_job.term_list
    page_list = db_job.page_list
    output_file_path = get_output_file(input_file.filename, term_list, page_list)
    case_sensitive = db_job.case_sensitive
    exact_page = db_job.exact_page

    # Stuff for Concurrency
    job_queue = mp.Manager().Queue()

    sub_jobs = []

    # Put listener to work first
    with mp.Pool() as process_pool:
        process_pool.apply_async(
            listener,
            (
                job_queue,
                output_file_path,
            ),
        )
        for input_url in input_urls:
            sub_job = process_pool.apply_async(
                process_url,
                (
                    input_url,
                    job_queue,
                    term_list,
                    page_list,
                    case_sensitive,
                    exact_page,
                ),
            )
            sub_jobs.append(sub_job)

        for sub_job in sub_jobs:
            sub_job.get()

        # now we are done, kill the listener
        job_queue.put("kill")
        process_pool.close()
        process_pool.join()
        finish_job(db_job, output_file_path)


def get_urls(input_file) -> list:
    """Parses the file-to-be-processed into a list of urls

    Args:
        input_file: StoredFile object from depot pckg

    Returns:
        _type_: list of stringified urls_
    """

    input_urls = []
    for line in input_file.read().decode("UTF-8").splitlines():
        if not re.match("(?:http|ftp|https)://", line):
            input_urls.append("http://{}".format(line))
        else:
            input_urls.append(line)
    input_file.close()

    return input_urls


def get_output_file(input_filename: str, term_list: list, page_list: list) -> str:
    """Generates headers, writes to output csv and returns file name

    Args:
        input_filename (str): the input file's filename
        term_list (list): list of terms to search homepage for
        page_list (list): list of named sub pages to search sitemap for

    Returns:
        str: Name of output csv file which is named and structed based on Job attributes.
    """

    path_to_output = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        f"{input_filename.rsplit('.',1)[0]}_{uuid.uuid4().hex}.csv",
    )
    # [sites, term_a, term_b, page_a, page_b]
    headers = (
        ["sites"]
        + list(map(lambda term: "term_" + term, term_list))
        + list(map(lambda page: "page_" + page, page_list))
    )

    with open(path_to_output, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    return path_to_output


def listener(job_queue: mp.Queue, output_file_path: str) -> None:
    """Continously write results from the other Processes calling process_url() to the output CSV.

    Args:
        job_queue (mp.Queue): queue of jobs that process_url() are passing results to
        output_file_path (str): output csv filepath
    """
    with open(output_file_path, "a") as f:
        while True:
            m = job_queue.get()
            if m == "kill":
                break
            f.write(str(m) + "\n")


def process_url(
    input_url: str,
    job_queue: mp.Queue,
    term_list: list,
    page_list: list,
    case_sensitive: bool,
    exact_page: bool,
) -> str:
    """Searches for terms given input_url and writes result to the job_queue along with pre-processed page_results

    Args:
        job (Job): object describing customizations for processing logic
        input_url (str): the url to search sitemaps in
        job_queue (mp.Queue): queue to pass finished jobs to _listener()

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
        job_queue.put(res)
        return res

    term_exist_list = find_terms_on_homepage(input_url, term_list, case_sensitive)
    page_exist_dict = find_pages_in_sitemap(input_url, page_list, exact_page)

    res = ",".join([input_url] + term_exist_list + list(page_exist_dict.values()))
    job_queue.put(res)
    return res


def find_terms_on_homepage(site: str, term_list: list, case_sensitive: bool) -> list:
    """Searches homepage of site for specified keywords

    Returns:
        list: list of boolean terms indicating presence of each keyword,
        corresponding to the header in __make_output_file()
    """
    print("looking for terms in home page...")
    term_exist_list = []

    with HTMLSession() as session:
        try:
            r = session.get(site, headers={"User-Agent": "Mozilla/5.0"})
        except requests.exceptions.RequestException as e:
            print(e)
            for term in term_list:
                term_exist_list.append("N/A")
            return term_exist_list
        try:
            r.html.render(timeout=15)
            for term in term_list:
                if term in r.html.html:
                    term_exist_list.append("True")
                else:
                    term_exist_list.append("False")
        except:
            print("Render attempt likely timed out")
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
        except:
            print("Failed to retrieve sitemap")

    print("searching sitemap")
    for page in tree.all_pages():
        potential_match = urlparse(page.url).path

        if len(potential_match) <= 1:
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


def finish_job(db_job: Job, output_file_path: str) -> None:
    with open(output_file_path, "rb") as f:
        db_job.output_file = f
    db.session.commit()
    try:
        os.remove(output_file_path)
    except OSError:
        pass
