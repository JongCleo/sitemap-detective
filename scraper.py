import os, sys
import csv
import requests
from bs4 import BeautifulSoup as bs
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


class Scraper:
    def __init__(self, test_mode, output_path, file_path, term_list, page_list):        
        ########################################################
        # Get scraper input, load sites into memory              
        if (test_mode):
            path_to_csv = "test_data/test.csv"
            term_list = ["connect", "integration"]
            page_list = ["connect", "integration"]
        else:
            path_to_csv = file_path            

            term_list = [
                x.strip()
                for x in term_list
            ]
            page_list = [
                x.strip() for x in page_list
            ]
        self.path_to_csv = path_to_csv
        self.term_list = term_list
        self.page_list = page_list
        self.output_path = output_path

    def processFile(self):
        self.__cleanOutput()
        # Prep output CSV
        input_urls = []

        with open(self.path_to_csv) as f:
            input_urls = f.read().splitlines()
                          
        header = ['sites'] + list(map(lambda term: "term_" + term, self.term_list)) + list(
            map(lambda page: "page_" + page, self.page_list))

        f = open(self.output_path, 'w')
        writer = csv.writer(f)
        writer.writerow(header)
        
        # Process Spreadsheet
        for site in input_urls:
            term_exist_list = []
            page_exist_dict = {self.page_list[i]: "False" for i in range(0, len(self.page_list))}

            # Look for terms in homepage
            try:
                r = requests.get(self.__prependHttp(site), headers={'User-Agent': 'Mozilla/5.0'})
                soup = bs(r.content, features="html.parser")

                for term in self.term_list:
                    if (len(soup(text=re.compile(term))) > 0):
                        term_exist_list.append('True')
                    else:
                        term_exist_list.append('False')

            except requests.exceptions.RequestException as e:
                print(e)

            # Look for pages in sitemap
            with HiddenPrints():
                tree = sitemap_tree_for_homepage(self.__prependHttp(site))
            for page in tree.all_pages():                                        
                if (page.url in self.page_list):
                    page_exist_dict[term] = "True"

            # write to file from memory
            writer.writerow([site] + term_exist_list + list(page_exist_dict.values()))

        f.close()
    
    def setPathToCSV(self):
        path_to_csv = "input/" + input('What is your file called?\n').strip()
        path_to_csv = path_to_csv + ".csv" if ".csv" not in path_to_csv else path_to_csv
        self.path_to_csv = path_to_csv
    def setTermList(self):
        self.term_list = [
            x.strip()
            for x in input('Enter comma separated terms to look for:\n').split(",")
        ]
    def setPageList(self):
        self.page_list = [
            x.strip() for x in input(
            'Enter comma separated page names to look for:\n').split(",")
        ]         

    def __cleanOutput(self):
        folder = 'output/'
        if (len(os.listdir(folder)) > 1):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)             
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    def __prependHttp(self, url):
        if not re.match('(?:http|ftp|https)://', url):
            return 'http://{}'.format(url)
        return url

