import os, sys
import re
import multiprocessing as mp
import csv
import uuid
import requests
from usp.tree import sitemap_tree_for_homepage
import logging
from urllib.parse import urlparse
from requests_html import HTMLSession
from futures3 import ThreadPoolExecutor, wait


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


class Job:
    """ADT containing filename and customizations for processing"""

    def __init__(
        self,
        filename: str,
        term_list: list,
        page_list: list,
        case_sensitive: bool = False,
        exact_page: bool = False,
    ):
        """_summary_

        Args:
            filename (str): Name of file to be processed
            term_list (list): List of keywords to search in homepages
            page_list (list): List of /subpages to search in sitemap
            case_sensitive (bool, optional): Determines case sensitivity while searching term_list terms in process_file().
            exact_page (bool, optional): Accepts substrings if True while searching page_list pages.
        """
        self.filename = filename
        self.term_list = [x.strip() for x in term_list]
        self.page_list = [x.strip() for x in page_list]
        self.case_sensitive = case_sensitive
        self.exact_page = exact_page


def process_file(job: Job) -> None:
    """Checks a list of domains for the existence of certain pages and keywords in each domains' sitemaps

    Args:
        job (Job): the job object containing the customization details of the job
    """

    input_urls = __get_urls(job.filename)
    path_to_output = __make_output_file(job)

    # The sitemap calls are IO bound I think...
    with ThreadPoolExecutor(max_workers=5) as executor:
        page_dict_list = executor.map(
            __find_pages_in_sitemap, input_urls, [job] * len(input_urls)
        )
    wait(page_dict_list)

    urls_and_page_search_results = zip(input_urls, page_dict_list)
    # Parallelism  setup for performance
    job_queue = mp.Manager().Queue()
    sub_jobs = []

    with mp.Pool() as process_pool:

        # Dedicated process for writing to output file
        process_pool.apply_async(
            __listener,
            (
                job_queue,
                path_to_output,
            ),
        )

        for result in urls_and_page_search_results:
            sub_job = process_pool.apply_async(
                __process_url, (result[0], result[1], job, job_queue)
            )
            sub_jobs.append(sub_job)

        for sub_job in sub_jobs:
            sub_job.get()

        # Done, kill the listener
        job_queue.put("kill")
        process_pool.close()
        process_pool.join()


def __listener(job_queue: mp.Queue, filename: str) -> None:
    """Continously write results from the other Processes calling process_url() to the output CSV.

    Args:
        job_queue (mp.Queue): queue of jobs that process_url() are passing results to
        filename (str): output csv filename
    """
    with open(filename, "a") as f:
        while True:
            m = job_queue.get()
            if m == "kill":
                break
            f.write(str(m) + "\n")


def __process_url(
    input_url: str, page_exist_dict: dict, job: Job, job_queue: mp.Queue
) -> str:
    """Searches for terms given input_url and writes result to the job_queue along with pre-processed page_results

    Args:
        input_url (str): the url to search sitemaps in
        job (Job): object describing customizations for processing logic
        job_queue (mp.Queue): queue to pass finished jobs to _listener()

    Returns:
        str: comma separated row of boolean values indicating whether search terms
        and pages were found for the given input_url. The order corresponds to the headers in __make_output_file()
    """

    if not __is_valid_url(input_url):
        res = ",".join(
            [input_url]
            + ["N/A" for i in range(len(job.term_list))]
            + ["N/A" for i in range(len(job.page_list))]
        )
        job_queue.put(res)
        return res

    term_exist_list = __find_terms_on_homepage(input_url, job)

    res = ",".join([input_url] + term_exist_list + list(page_exist_dict.values()))
    job_queue.put(res)
    return res


def __get_urls(filename: str) -> list:
    """Parses the file-to-be-processed into a list of urls

    Args:
        filename (str): The uploaded file; A single column csv of urls.

    Returns:
        _type_: list of stringified urls_
    """
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_file = os.path.join(cwd, "./uploads", filename)
    with open(path_to_file) as f:
        input_urls = []
        for line in f.read().splitlines():
            if not re.match("(?:http|ftp|https)://", line):
                input_urls.append("http://{}".format(line))
            else:
                input_urls.append(line)
    return input_urls


def __make_output_file(job: Job) -> str:
    """Generates headers, writes to output csv and returns file name

    Args:
        job (Job): Job object containing the terms and pages used in headers

    Returns:
        str: Name of output csv file which is named and structed based on Job attributes.
    """
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_output = os.path.join(
        cwd, "./output", f"{job.filename.rsplit('.',1)[0]}_{uuid.uuid4().hex}.csv"
    )

    headers = (
        ["sites"]
        + list(map(lambda term: "term_" + term, job.term_list))
        + list(map(lambda page: "page_" + page, job.page_list))
    )

    with open(path_to_output, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

    return path_to_output


def __find_terms_on_homepage(site: str, job: Job) -> list:
    """Searches homepage of site for specified keywords

    Args:
        site (str): url of site to be searched
        job (Job): ADT containing the keywords to search for

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
            for term in job.term_list:
                term_exist_list.append("N/A")
            return term_exist_list
        try:
            r.html.render(timeout=15)
            for term in job.term_list:
                if term in r.html.html:
                    term_exist_list.append("True")
                else:
                    term_exist_list.append("False")
        except:
            print("Render attempt likely timed out")
            for term in job.term_list:
                term_exist_list.append("N/A")

    return term_exist_list


def __find_pages_in_sitemap(site: str, job: Job) -> dict:
    """Searches sitemap(s) of site for specified subpages

    Args:
        site (str): url of site to be searched
        job (Job): ADT containing the subpages to search for

    Returns:
        dict: dict of boolean terms indicating presence of each subpage,
        corresponding to the header in __make_output_file()
    """
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


def __is_valid_url(url: str) -> bool:
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
