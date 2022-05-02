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
from helper_functions import is_valid_url, get_upload_directory, get_output_directory


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
    """Class containing ADT for storing customizations and processing method"""

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

    def process_file(self) -> None:
        """Checks a list of domains for the existence of certain pages and keywords in each domains' sitemaps"""

        input_urls = self.__get_urls()
        path_to_output = self.__make_output_file()

        # Stuff for Concurrency
        job_queue = mp.Manager().Queue()

        sub_jobs = []

        # Put listener to work first
        with mp.Pool() as process_pool:
            process_pool.apply_async(
                listener,
                (
                    job_queue,
                    path_to_output,
                ),
            )

            for input_url in input_urls:
                sub_job = process_pool.apply_async(
                    process_url, (self, input_url, job_queue)
                )
                sub_jobs.append(sub_job)

            for sub_job in sub_jobs:
                sub_job.get()

            # now we are done, kill the listener
            job_queue.put("kill")
            process_pool.close()
            process_pool.join()

    def __get_urls(self) -> list:
        """Parses the file-to-be-processed into a list of urls

        Args:
            filename (str): The uploaded file; A single column csv of urls.

        Returns:
            _type_: list of stringified urls_
        """
        path_to_file = get_upload_directory()
        with open(path_to_file) as f:
            input_urls = []
            for line in f.read().splitlines():
                if not re.match("(?:http|ftp|https)://", line):
                    input_urls.append("http://{}".format(line))
                else:
                    input_urls.append(line)
        return input_urls

    def __make_output_file(self) -> str:
        """Generates headers, writes to output csv and returns file name

        Returns:
            str: Name of output csv file which is named and structed based on Job attributes.
        """

        path_to_output = os.path.join(
            get_output_directory(),
            f"{self.filename.rsplit('.',1)[0]}_{uuid.uuid4().hex}.csv",
        )
        # [sites, term_a, term_b, page_a, page_b]
        headers = (
            ["sites"]
            + list(map(lambda term: "term_" + term, self.term_list))
            + list(map(lambda page: "page_" + page, self.page_list))
        )

        with open(path_to_output, "w") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

        return path_to_output

    def find_terms_on_homepage(self, site: str) -> list:
        """Searches homepage of site for specified keywords

        Args:
            site (str): url of site to be searched

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
                for term in self.term_list:
                    term_exist_list.append("N/A")
                return term_exist_list
            try:
                r.html.render(timeout=15)
                for term in self.term_list:
                    if term in r.html.html:
                        term_exist_list.append("True")
                    else:
                        term_exist_list.append("False")
            except:
                print("Render attempt likely timed out")
                for term in self.term_list:
                    term_exist_list.append("N/A")

        return term_exist_list

    def find_pages_in_sitemap(self, site: str) -> dict:
        """Searches sitemap(s) of site for specified subpages

        Args:
            site (str): url of site to be searched

        Returns:
            dict: dict of boolean terms indicating presence of each subpage,
            corresponding to the header in __make_output_file()
        """
        page_exist_dict = {pg: "False" for pg in self.page_list}
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
                if (self.exact_page and search_term == potential_match) or (
                    not self.exact_page and search_term in potential_match
                ):
                    page_exist_dict[search_term] = "True"

        return page_exist_dict


###### MP Methods placed outside of class
###### See https://stackoverflow.com/questions/44185770/call-multiprocessing-in-class-method-python


def listener(job_queue: mp.Queue, filename: str) -> None:
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


def process_url(job: Job, input_url: str, job_queue: mp.Queue) -> str:
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
            + ["N/A" for i in range(len(job.term_list))]
            + ["N/A" for i in range(len(job.page_list))]
        )
        job_queue.put(res)
        return res

    term_exist_list = job.find_terms_on_homepage(input_url)
    page_exist_dict = job.find_pages_in_sitemap(input_url)

    res = ",".join([input_url] + term_exist_list + list(page_exist_dict.values()))
    job_queue.put(res)
    return res
