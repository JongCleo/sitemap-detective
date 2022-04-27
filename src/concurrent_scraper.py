import os, sys
import multiprocessing as mp
import csv
import uuid
import requests
from usp.tree import sitemap_tree_for_homepage
from usp.exceptions import TimeoutException
import logging
from urllib.parse import urlparse
from requests_html import HTMLSession
from helper_functions import __prepend_http, __is_valid_url


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        logging.disable(logging.CRITICAL)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        logging.disable(logging.NOTSET)


class Job:
    def __init__(
        self, filename, term_list, page_list, case_sensitive=False, exact_page=False
    ):
        self.filename = filename
        self.term_list = [x.strip() for x in term_list]
        self.page_list = [x.strip() for x in page_list]
        self.case_sensitive = case_sensitive
        self.exact_page = exact_page


def concurrent_process_file(job: Job) -> None:

    print("reading in input urls")
    input_urls = __get_urls(job.filename)
    print("preparing file")
    path_to_output = __make_output_file(job)

    # Stuff for Concurrency
    manager = mp.Manager()
    job_queue = manager.Queue()
    pool = mp.Pool()
    sub_jobs = []

    # Put listener to work first
    pool.apply_async(
        listener,
        (
            job_queue,
            path_to_output,
        ),
    )

    for input_url in input_urls:
        sub_job = pool.apply_async(process_url, (input_url, job, job_queue))
        sub_jobs.append(sub_job)

    for sub_job in sub_jobs:
        sub_job.get()

    # now we are done, kill the listener
    job_queue.put("kill")
    pool.close()
    pool.join()


def listener(job_queue, filename):
    """listens for messages on the queue, writes to file."""

    with open(filename, "a") as f:
        while True:
            m = job_queue.get()
            if m == "kill":
                break
            f.write(str(m) + "\n")


def process_url(input_url: str, job: Job, job_queue):
    """find term and page matches for the url"""

    input_url = __prepend_http(input_url)
    if not __is_valid_url(input_url):
        return (
            [input_url]
            + ["N/A" for i in range(len(job.term_list))]
            + ["N/A" for i in range(len(job.page_list))]
        )

    print("looking for terms in home page...")
    term_exist_list = __find_terms_on_homepage(input_url, job)
    print("looking for pages in sitemap...")
    page_exist_dict = __find_pages_in_sitemap(input_url, job)

    res = ",".join([input_url] + term_exist_list + list(page_exist_dict.values()))
    job_queue.put(res)
    return res


def __get_urls(filename: str):
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_file = os.path.join(cwd, "../uploads", filename)
    with open(path_to_file) as f:
        input_urls = f.read().splitlines()
    return input_urls


def __make_output_file(job: Job):
    """
    generates headers and writes to output file and returns file name
    """
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_output = os.path.join(
        cwd, "../output", f"{job.filename.rsplit('.',1)[0]}_{uuid.uuid4().hex}.csv"
    )
    # [sites, term_a, term_b, page_a, page_b]
    headers = (
        ["sites"]
        + list(map(lambda term: "term_" + term, job.term_list))
        + list(map(lambda page: "page_" + page, job.page_list))
    )

    with open(path_to_output, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    return path_to_output


def __find_terms_on_homepage(site: str, job: Job):
    term_exist_list = []

    with HTMLSession() as session:
        try:
            r = session.get(site, headers={"User-Agent": "Mozilla/5.0"})
        except requests.exceptions.RequestException as e:
            print(e)
        try:
            r.html.render(timeout=15)
            for term in job.term_list:
                if term in r.html.html:
                    term_exist_list.append("True")
                else:
                    term_exist_list.append("False")
        except:
            print("Likely timed out")
            for term in job.term_list:
                term_exist_list.append("N/A")

    return term_exist_list


def __find_pages_in_sitemap(site: str, job: Job):
    page_exist_dict = {pg: "False" for pg in job.page_list}
    print("loading sitemap")
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
            if (job.exact_page and search_term == potential_match) or (
                not job.exact_page and search_term in potential_match
            ):
                page_exist_dict[search_term] = "True"

    return page_exist_dict
