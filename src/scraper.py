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
    def __init__(self, filename, term_list, page_list):
        self.filename = filename
        self.term_list = [x.strip() for x in term_list]
        self.page_list = [x.strip() for x in page_list]


def process_file(job):

    ####### Get Path to file
    # TODO: abstract the reading process away from local vs cloud
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_file = os.path.join(cwd, "../uploads", job.filename)
    path_to_output = os.path.join(
        cwd, "../output", f"{job.filename}_{uuid.uuid4().hex}"
    )

    ###### Load urls in Memory
    with open(path_to_file) as f:
        input_urls = f.read().splitlines()

    ##### Scaffold the Output CSV
    # [sites, term_a, term_b, page_a, page_b]
    headers = (
        ["sites"]
        + list(map(lambda term: "term_" + term, job.term_list))
        + list(map(lambda page: "page_" + page, job.page_list))
    )

    with open(path_to_output, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        # Process URLs
        for site in input_urls:
            term_exist_list = []
            page_exist_dict = {pg: "False" for pg in job.page_list}
            site = __prepend_http(site)

            # Look for terms in homepage
            try:
                session = HTMLSession()
                r = session.get(site, headers={"User-Agent": "Mozilla/5.0"})
                r.html.render(timeout=20)

                for term in job.term_list:
                    if term in r.html.html:
                        term_exist_list.append("True")
                    else:
                        term_exist_list.append("False")

            except requests.exceptions.RequestException as e:
                print(e)

            # Look for pages in sitemap
            with HiddenPrints():
                tree = sitemap_tree_for_homepage(site)
            for page in tree.all_pages():
                search_term = urlparse(page.url).path

                search_term = search_term[1:] if search_term[0] == "/" else search_term
                if search_term in job.page_list:
                    page_exist_dict[search_term] = "True"

            # write to file from memory
            writer.writerow([site] + term_exist_list + list(page_exist_dict.values()))


def __prepend_http(url):
    if not re.match("(?:http|ftp|https)://", url):
        return "http://{}".format(url)
    return url


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
    filename = input("What is your file called?\n").strip()
    filename = filename + ".csv" if ".csv" not in filename else filename

    term_list = [
        x.strip()
        for x in input("Enter comma separated terms to look for:\n").split(",")
    ]

    page_list = [
        x.strip()
        for x in input("Enter comma separated page names to look for:\n").split(",")
    ]

    job = Job(filename, term_list, page_list)
    profile = cProfile.Profile()
    profile.runcall(process_file, job)
    ps = pstats.Stats(profile)
    ps.sort_stats("cumtime")
    ps.print_stats(20)


if __name__ == "__main__":
    main()
