import cProfile
import os, sys
import pstats
import csv
import uuid
import requests
import re
from usp.tree import sitemap_tree_for_homepage
import logging
from urllib.parse import urlparse
from requests_html import HTMLSession


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


def process_file(job: Job) -> None:
    print("reading in input urls")
    input_urls = __get_urls(job.filename)
    print("preparing file")
    path_to_output = __make_output_file(job)

    with open(path_to_output, "a") as f:
        writer = csv.writer(f)

        for input_url in input_urls:
            input_url = __prepend_http(input_url)
            if not __is_valid_url(input_url):
                writer.writerow(
                    [input_url]
                    + ["N/A" for i in range(len(job.term_list))]
                    + ["N/A" for i in range(len(job.page_list))]
                )
                continue
            print("looking for terms in home page...")
            term_exist_list = __find_terms_on_homepage(input_url, job)
            print("looking for pages in sitemap...")
            page_exist_dict = __find_pages_in_sitemap(input_url, job)
            writer.writerow(
                [input_url] + term_exist_list + list(page_exist_dict.values())
            )


def __get_urls(filename: str):
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_file = os.path.join(cwd, "../uploads", filename)
    with open(path_to_file) as f:
        input_urls = f.read().splitlines()
    return input_urls


# method generates headers and writes lines to output file and returns file name
def __make_output_file(job: Job):
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
    try:
        with HTMLSession() as session:
            r = session.get(site, headers={"User-Agent": "Mozilla/5.0"})
            r.html.render(timeout=15)
            for term in job.term_list:
                if term in r.html.html:
                    term_exist_list.append("True")
                else:
                    term_exist_list.append("False")

    except requests.exceptions.RequestException as e:
        print(e)

    return term_exist_list


def __find_pages_in_sitemap(site: str, job: Job):
    page_exist_dict = {pg: "False" for pg in job.page_list}

    with HiddenPrints():
        try:
            tree = sitemap_tree_for_homepage(site)
        except:
            print("Failed to retrieve sitemap")
    for page in tree.all_pages():
        potential_match = urlparse(page.url).path
        potential_match = (
            potential_match[1:] if potential_match[0] == "/" else potential_match
        )
        for search_term in page_exist_dict:
            if search_term in potential_match:
                print(search_term)
                print(potential_match)
            if (job.exact_page and search_term == potential_match) or (
                not job.exact_page and search_term in potential_match
            ):
                page_exist_dict[search_term] = "True"

    return page_exist_dict


def __prepend_http(url: str):
    if not re.match("(?:http|ftp|https)://", url):
        return "http://{}".format(url)
    return url


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


def main():
    clean_output_directory()
    filename = "small_test.csv"
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    job = Job(filename, term_list, page_list)

    # Act
    process_file(job)
    # profile = cProfile.Profile()
    # profile.runcall(process_file, job)
    # ps = pstats.Stats(profile)
    # ps.sort_stats("cumtime")
    # ps.print_stats(20)


if __name__ == "__main__":
    main()
