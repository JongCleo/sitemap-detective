import os, sys
import csv
import requests
from bs4 import BeautifulSoup as bs
import uuid
import re
from usp.tree import sitemap_tree_for_homepage
import logging

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        logging.disable(logging.CRITICAL)

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
        logging.disable(logging.NOTSET)


########################################################
# Get scraper input, load sites into memory

if (True):
    path_to_csv = "input/test.csv"
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]
else:
    path_to_csv = "input/" + input('What is your file called?\n').strip()

    path_to_csv = path_to_csv + ".csv" if ".csv" not in path_to_csv else path_to_csv

    term_list = [
        x.strip()
        for x in input('Enter comma separated terms to look for:\n').split(",")
    ]
    page_list = [
        x.strip() for x in input(
            'Enter comma separated page names to look for:\n').split(",")
    ]

input_urls = []

with open(path_to_csv) as f:
    input_urls = f.read().splitlines()

########################################################
# Prep output CSV
output_name = "output_csv_" + str(uuid.uuid1()) + ".csv"
header = ['sites'] + list(map(lambda term: "term_" + term, term_list)) + list(
    map(lambda page: "page_" + page, page_list))

f = open('output/' + output_name, 'w')
writer = csv.writer(f)
writer.writerow(header)


########################################################
# Process URLs
def prependHttp(url):
    if not re.match('(?:http|ftp|https)://', url):
        return 'http://{}'.format(url)
    return url


for site in input_urls:

    term_exist_list = []
    page_exist_dict = {page_list[i]: "False" for i in range(0, len(page_list))}

    # look for terms in homepage
    try:
        r = requests.get(prependHttp(site), headers={'User-Agent': 'Mozilla/5.0'})
        soup = bs(r.content, features="html.parser")

        for term in term_list:
            if (len(soup(text=re.compile(term))) > 0):
                term_exist_list.append('True')
            else:
                term_exist_list.append('False')

    except requests.exceptions.RequestException as e:
        print(e)

    # get sitemap, look for match in sitemap
    with HiddenPrints():
        tree = sitemap_tree_for_homepage(prependHttp(site))
    for page in tree.all_pages():
        for term in page_list:
            if (term in page.url):
                page_exist_dict[term] = "True"

    # write to file from memory
    writer.writerow([site] + term_exist_list + list(page_exist_dict.values()))

f.close()
